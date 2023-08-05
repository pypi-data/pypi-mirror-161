from __future__ import annotations

import json
import re
from typing import Optional

import numpy as np
import pandas as pd
from seeq.sdk import *

from seeq.base.seeq_names import SeeqNames
from seeq.spy import _common, _login
from seeq.spy._common import EMPTY_GUID
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status


def push(session: Session, metadata, workbook_id, datasource_output, sync_token, errors, status):
    items_api = ItemsApi(session.client)
    trees_api = TreesApi(session.client)

    metadata_df = metadata  # type: pd.DataFrame

    timer = _common.timer_start()

    status_columns = [
        'Signal',
        'Scalar',
        'Condition',
        'Threshold Metric',
        'Asset',
        'Relationship',
        'Overall',
        'Time'
    ]

    status_dict = dict()
    for status_column in status_columns:
        status_dict[status_column] = 0

    status.df = pd.DataFrame([status_dict], index=['Items pushed'])

    status.update('Pushing metadata to datasource <strong>%s [%s]</strong> scoped to workbook ID '
                  '<strong>%s</strong>' % (
                      datasource_output.name, datasource_output.datasource_id, workbook_id),
                  Status.RUNNING)

    total = len(metadata_df)

    def _print_push_progress():
        status.df['Time'] = _common.timer_elapsed(timer)
        status.update('Pushing metadata to datasource <strong>%s [%s]</strong> scoped to workbook ID '
                      '<strong>%s</strong>' % (
                          datasource_output.name, datasource_output.datasource_id, workbook_id),
                      Status.RUNNING)

    flush_now = False
    cache = dict()
    roots = dict()
    batch_size = 1000
    put_signals_input = PutSignalsInputV1()
    put_signals_input.signals = list()
    put_scalars_input = PutScalarsInputV1()
    put_scalars_input.scalars = list()
    condition_batch_input = ConditionBatchInputV1()
    condition_batch_input.conditions = list()
    threshold_metric_inputs = list()
    asset_batch_input = AssetBatchInputV1()
    asset_batch_input.assets = list()
    tree_batch_input = AssetTreeBatchInputV1()
    tree_batch_input.relationships = list()
    tree_batch_input.parent_host_id = datasource_output.id
    tree_batch_input.child_host_id = datasource_output.id
    last_scalar_datasource = None

    _common.validate_unique_dataframe_index(metadata_df, 'metadata')

    # Make sure the columns of the dataframe can accept anything we put in them since metadata_df might have specific
    # dtypes.
    push_results_df = metadata_df.copy().astype(object)
    if 'Type' not in push_results_df.columns:
        push_results_df['Type'] = pd.Series(np.nan, dtype='object')

    # Workbooks will get processed outside of this function
    push_results_df = push_results_df[~push_results_df['Type'].isin(['Workbook'])]

    if 'Push Result' in push_results_df:
        push_results_df = push_results_df.drop(columns=['Push Result'])

    while True:
        dependencies_not_found = list()
        at_least_one_item_created = False

        for index, row in push_results_df.iterrows():
            if 'Push Result' in row and not pd.isna(row['Push Result']):
                continue

            status.df['Overall'] += 1

            try:
                flush_now, last_scalar_datasource = \
                    _process_push_row(session, asset_batch_input, cache, condition_batch_input, status,
                                      datasource_output, flush_now, index, last_scalar_datasource, push_results_df,
                                      put_scalars_input, put_signals_input, roots, row, sync_token, tree_batch_input,
                                      workbook_id, threshold_metric_inputs, errors)

            except SPyDependencyNotFound as e:
                dependencies_not_found.append((index, e))
                continue

            except Exception as e:
                if errors == 'raise':
                    raise

                total -= 1
                push_results_df.at[index, 'Push Result'] = str(e)
                continue

            at_least_one_item_created = True

            if int(status.df['Overall']) % batch_size == 0 or flush_now:
                _print_push_progress()

                _flush(session, put_signals_input, put_scalars_input, condition_batch_input, threshold_metric_inputs,
                       asset_batch_input, tree_batch_input, push_results_df, errors)

                flush_now = False

        _print_push_progress()

        _flush(session, put_signals_input, put_scalars_input, condition_batch_input, threshold_metric_inputs,
               asset_batch_input, tree_batch_input, push_results_df, errors)

        if len(dependencies_not_found) == 0:
            break

        if not at_least_one_item_created:
            missing_items_str = ''
            for not_found_index, not_found_data_id in dependencies_not_found:
                push_results_df.at[not_found_index, 'Push Result'] = 'Could not find dependency %s' % not_found_data_id
                missing_items_str += str(not_found_data_id) + ' '

            if errors == 'raise':
                raise SPyRuntimeError('Could not find all dependencies -- check "Push Result" column for error '
                                      'details \nMissing items: ' + missing_items_str)

            break

    for asset_input in roots.values():
        results = items_api.search_items(filters=['Datasource Class==%s && Datasource ID==%s && Data ID==%s' % (
            datasource_output.datasource_class, datasource_output.datasource_id,
            asset_input.data_id)])  # type: ItemSearchPreviewPaginatedListV1
        if len(results.items) == 0:
            raise SPyRuntimeError('Root item "%s" not found' % asset_input.name)
        item_id_list = ItemIdListInputV1()
        item_id_list.items = [results.items[0].id]
        trees_api.move_nodes_to_root_of_tree(body=item_id_list)

    status.df['Time'] = _common.timer_elapsed(timer)
    status.update(f'Pushed metadata successfully to datasource <strong>{datasource_output.name} '
                  f'[{datasource_output.datasource_id}]</strong> scoped to workbook ID <strong>{workbook_id}</strong>',
                  Status.SUCCESS)

    return push_results_df


def _process_push_row(session: Session, asset_batch_input, cache, condition_batch_input, status, datasource_output,
                      flush_now, index, last_scalar_datasource, push_results_df, put_scalars_input, put_signals_input,
                      roots, row, sync_token, tree_batch_input, workbook_id, threshold_metric_inputs, errors):
    row_dict = row.to_dict()
    items_api = ItemsApi(session.client)

    if _common.present(row_dict, 'Path'):
        row_dict['Path'] = _common.sanitize_path_string(row_dict['Path'])

    if not _common.present(row_dict, 'Name'):
        raise SPyRuntimeError('Metadata must have a "Name" column.')

    if _common.get(row_dict, 'Reference') is True:
        if not _common.present(row_dict, 'ID'):
            raise SPyRuntimeError('"ID" column required when "Reference" column is True')
        build_reference(session, row_dict)

    # Set 'Cache Enabled' to False for jump tags
    if isinstance(_common.get(row_dict, 'Formula'), str) and re.match(r'^\s*\$\w+\s*$', row_dict['Formula']):
        row_dict['Cache Enabled'] = False

    row_dict['Scoped To'] = workbook_id

    if not _common.present(row_dict, 'Type') or not _is_handled_type(row_dict['Type']):
        if not _common.present(row_dict, 'Formula'):
            _common.raise_or_catalog(errors, df=push_results_df, column='Push Result', index=index,
                                     exception_type=SPyRuntimeError,
                                     message='Items with no valid type specified cannot be pushed unless they are '
                                             'calculations. "Formula" column is required for such items.')
        else:
            formula = _common.get(row_dict, 'Formula')
            if _common.present(row_dict, 'Formula Parameters'):
                formula_parameters = _process_formula_parameters(_common.get(row_dict, 'Formula Parameters'),
                                                                 workbook_id,
                                                                 push_results_df)
            else:
                formula_parameters = []

            try:
                formulas_api = FormulasApi(session.client)
                formula_compile_output = formulas_api.compile_formula(formula=formula, parameters=formula_parameters)
                if formula_compile_output.errors or formula_compile_output.return_type == '':
                    _common.raise_or_catalog(errors, df=push_results_df, column='Push Result', index=index,
                                             exception_type=SPyRuntimeError,
                                             message=f'Formula compilation failed with message: '
                                                     f'{formula_compile_output.status_message}')
                    return flush_now, last_scalar_datasource
                else:
                    row_dict['Type'] = formula_compile_output.return_type
                    push_results_df.at[index, 'Type'] = formula_compile_output.return_type
            except ApiException as e:
                _common.raise_or_catalog(errors, df=push_results_df, column='Push Result', index=index, e=e)

    if _common.present(push_results_df.loc[index], 'Push Result'):
        return flush_now, last_scalar_datasource

    scoped_data_id = get_scoped_data_id(row_dict, workbook_id)
    if not _common.present(row_dict, 'Datasource Class'):
        row_dict['Datasource Class'] = datasource_output.datasource_class

    if not _common.present(row_dict, 'Datasource ID'):
        row_dict['Datasource ID'] = datasource_output.datasource_id

    def _set_properties_by_id():
        _row_sync_token = sync_token if _needs_sync_token(session, row_dict) else None
        _set_item_properties(session, row_dict, _row_sync_token)
        _set_existing_item_push_results(session, index, push_results_df, row_dict)

    if 'Signal' in row_dict['Type']:
        signal_input = SignalInputV1() if _common.present(row_dict, 'ID') else SignalWithIdInputV1()

        dict_to_signal_input(row_dict, signal_input)

        signal_input.formula_parameters = _process_formula_parameters(signal_input.formula_parameters,
                                                                      workbook_id,
                                                                      push_results_df)
        if len(signal_input.formula_parameters) > 0:
            push_results_df.at[index, 'Formula Parameters'] = signal_input.formula_parameters

        if signal_input.formula:
            # There are lots of calculated properties that must be None for Appserver to accept our input
            signal_input.maximum_interpolation = None
            signal_input.interpolation_method = None
            signal_input.key_unit_of_measure = None
            signal_input.value_unit_of_measure = None

        if _common.present(row_dict, 'ID'):
            status.df['Signal'] += 1
            if _needs_sync_token(session, row_dict):
                signal_input.sync_token = sync_token

            # Unfortunately we can't use the _set_item_properties(d) function like we can for Scalar and Condition
            # because we are not allowed to directly set the Value Unit Of Measure.
            try:
                signals_api = SignalsApi(session.client)
                try:
                    signal_output = signals_api.put_signal(id=row_dict['ID'], body=signal_input)
                except ApiException as e:
                    if SeeqNames.API.ErrorMessages.attempted_to_set_scope_on_a_globally_scoped_item in str(e):
                        # This handles CRAB-25450 by forcing global scope if we encounter the error.
                        signal_input.scoped_to = None
                        signal_output = signals_api.put_signal(id=row_dict['ID'],
                                                               body=signal_input)  # type: SignalOutputV1
                    else:
                        raise

                _push_ui_config(session, signal_input, signal_output)

                # For some reason this is the only way to override Maximum Interpolation
                if _common.present(row_dict, SeeqNames.Properties.override_maximum_interpolation):
                    items_api.set_property(id=row_dict['ID'],
                                           property_name=SeeqNames.Properties.override_maximum_interpolation,
                                           body=PropertyInputV1(
                                               value=row_dict[SeeqNames.Properties.override_maximum_interpolation]))

                # For some reason overriding Number Format doesn't follow the same pattern as for Maximum
                # Interpolation. But SPy will harmonize it so that it's the same.
                if _common.present(row_dict, 'Override ' + SeeqNames.Properties.number_format):
                    items_api.set_property(id=row_dict['ID'],
                                           property_name=SeeqNames.Properties.number_format,
                                           body=PropertyInputV1(
                                               value=row_dict['Override ' + SeeqNames.Properties.number_format]))

                _set_existing_item_push_results(session, index, push_results_df, row_dict, signal_output)
            except ApiException as e:
                _common.raise_or_catalog(errors, df=push_results_df, index=index, column='Push Result', e=e)
        else:
            signal_input.datasource_class = row_dict['Datasource Class']
            signal_input.datasource_id = row_dict['Datasource ID']
            signal_input.data_id = scoped_data_id
            signal_input.sync_token = sync_token
            setattr(signal_input, 'dataframe_index', index)
            status.df['Signal'] += _add_no_dupe(put_signals_input.signals, signal_input)

    elif 'Scalar' in row_dict['Type']:
        scalar_input = ScalarInputV1()

        dict_to_scalar_input(row_dict, scalar_input)

        scalar_input.parameters = _process_formula_parameters(scalar_input.parameters, workbook_id, push_results_df)
        row_dict['Formula Parameters'] = scalar_input.parameters
        if len(scalar_input.parameters) > 0:
            push_results_df.at[index, 'Formula Parameters'] = scalar_input.parameters

        if _common.present(row_dict, 'ID'):
            status.df['Scalar'] += 1
            _set_properties_by_id()
        else:
            put_scalars_input.datasource_class = row_dict['Datasource Class']
            put_scalars_input.datasource_id = row_dict['Datasource ID']
            scalar_input.data_id = scoped_data_id
            scalar_input.sync_token = sync_token
            setattr(scalar_input, 'dataframe_index', index)
            status.df['Scalar'] += _add_no_dupe(put_scalars_input.scalars, scalar_input)

            # Since with scalars we have to put the Datasource Class and Datasource ID on the batch, we have to
            # recognize if it changed and, if so, flush the current batch.
            if last_scalar_datasource is not None and \
                    last_scalar_datasource != (row_dict['Datasource Class'], row_dict['Datasource ID']):
                flush_now = True

            last_scalar_datasource = (row_dict['Datasource Class'], row_dict['Datasource ID'])

    elif 'Condition' in row_dict['Type']:
        condition_input = ConditionInputV1()
        dict_to_condition_input(row_dict, condition_input)

        condition_input.parameters = _process_formula_parameters(condition_input.parameters, workbook_id,
                                                                 push_results_df)
        row_dict['Formula Parameters'] = condition_input.parameters
        if len(condition_input.parameters) > 0:
            push_results_df.at[index, 'Formula Parameters'] = condition_input.parameters

        if condition_input.formula is None and condition_input.maximum_duration is None:
            raise SPyRuntimeError('"Maximum Duration" column required for stored conditions')

        if _common.present(row_dict, 'Capsule Property Units'):
            condition_input.capsule_properties = [CapsulePropertyInputV1(name, uom) for name, uom in
                                                  row_dict['Capsule Property Units'].items()]

        if _common.present(row_dict, 'ID'):
            status.df['Condition'] += 1
            if _common.present(row_dict, 'Capsule Property Units'):
                status.warn("Updating condition's Capsule Property Units by ID is not supported yet.")
            _set_properties_by_id()
        else:
            condition_input.datasource_class = row_dict['Datasource Class']
            condition_input.datasource_id = row_dict['Datasource ID']
            condition_input.data_id = scoped_data_id
            condition_input.sync_token = sync_token
            setattr(condition_input, 'dataframe_index', index)
            status.df['Condition'] += _add_no_dupe(condition_batch_input.conditions, condition_input)

    elif row_dict['Type'] == 'Asset':
        if _common.present(row_dict, 'ID'):
            status.df['Asset'] += 1
            _set_properties_by_id()
        else:
            asset_input = AssetInputV1()
            dict_to_asset_input(row_dict, asset_input)
            asset_input.data_id = scoped_data_id
            asset_input.sync_token = sync_token
            setattr(asset_input, 'dataframe_index', index)
            status.df['Asset'] += _add_no_dupe(asset_batch_input.assets, asset_input, overwrite=True)
            asset_batch_input.host_id = datasource_output.id
            if _common.present(row_dict, 'Path') and len(row_dict['Path']) == 0:
                roots[asset_input.data_id] = asset_input

    elif 'Metric' in row_dict['Type']:
        threshold_metric_input = ThresholdMetricInputV1()
        if _common.get(row_dict, 'Formula') == '<ThresholdMetric>':
            threshold_metric_input = threshold_metric_input_from_formula_parameters(
                _common.get(row_dict, 'Formula Parameters'))
            dict_to_threshold_metric_input(row_dict, threshold_metric_input)
        else:
            dict_to_threshold_metric_input(row_dict, threshold_metric_input)
            _set_threshold_levels_from_system(session, threshold_metric_input)
            if threshold_metric_input.measured_item:
                threshold_metric_input.measured_item = _item_id_from_parameter_value(
                    threshold_metric_input.measured_item, workbook_id, push_results_df)
            if threshold_metric_input.bounding_condition:
                threshold_metric_input.bounding_condition = _item_id_from_parameter_value(
                    threshold_metric_input.bounding_condition, workbook_id, push_results_df)

            threshold_metric_input.thresholds = _convert_thresholds_dict_to_input(threshold_metric_input.thresholds,
                                                                                  workbook_id, push_results_df)

            if _common.present(row_dict, 'Statistic'):
                threshold_metric_input.aggregation_function = _common.statistic_to_aggregation_function(
                    row_dict['Statistic'])
                push_results_df.at[index, 'Aggregation Function'] = threshold_metric_input.aggregation_function

        if _common.present(row_dict, 'ID'):
            metrics_api = MetricsApi(session.client)
            metrics_api.put_threshold_metric(id=row_dict['ID'], body=threshold_metric_input)
            _set_existing_item_push_results(session, index, push_results_df, row_dict)
            status.df['Threshold Metric'] += 1
        else:
            threshold_metric_input.datasource_class = row_dict['Datasource Class']
            threshold_metric_input.datasource_id = row_dict['Datasource ID']
            threshold_metric_input.data_id = scoped_data_id
            threshold_metric_input.sync_token = sync_token
            setattr(threshold_metric_input, 'dataframe_index', index)
            status.df['Threshold Metric'] += _add_no_dupe(threshold_metric_inputs, threshold_metric_input)

        push_results_df.at[index, 'Push Result'] = 'Success'

    path = determine_path(row_dict)
    if path:
        _reify_path(path, workbook_id, datasource_output, scoped_data_id, cache, roots, asset_batch_input,
                    tree_batch_input, sync_token, status, index)
    return flush_now, last_scalar_datasource


def _push_ui_config(session: Session, input_object, item):
    if not hasattr(input_object, '_ui_config'):
        return

    items_api = ItemsApi(session.client)
    items_api.set_property(id=item.id,
                           property_name='UIConfig',
                           body=PropertyInputV1(value=getattr(input_object, '_ui_config')))


def _set_item_properties(session: Session, row_dict, sync_token):
    items_api = ItemsApi(session.client)

    do_not_exclude = [
        SeeqNames.Properties.name,
        SeeqNames.Properties.description,
        SeeqNames.Properties.interpolation_method,
        SeeqNames.Properties.value_uom,
        SeeqNames.Properties.uom,
        SeeqNames.Properties.number_format
    ]

    if _common.get(row_dict, 'Type') == 'StoredCondition':
        # We can't set this on calculated conditions but we can (and want to) on stored conditions
        do_not_exclude.append(SeeqNames.Properties.maximum_duration)

    excluded_properties = [p for p in IGNORED_PROPERTIES if p not in do_not_exclude]

    props = [
        ScalarPropertyV1(name=_name, value=_value) for _name, _value in row_dict.items()
        if _name not in excluded_properties and (isinstance(_value, list) or not pd.isna(_value))
    ]
    if sync_token:
        props.append(ScalarPropertyV1(name=SeeqNames.Properties.sync_token, value=sync_token))

    item_output = items_api.set_properties(id=row_dict['ID'], body=props)

    if item_output.scoped_to is not None and 'Scoped To' in row_dict:
        # This handles CRAB-25450 by only attempting to set scope if the item is not already globally scoped
        scoped_to = _common.get(row_dict, 'Scoped To')
        if scoped_to is not None:
            items_api.set_scope(id=row_dict['ID'], workbook_id=scoped_to)
        else:
            items_api.set_scope(id=row_dict['ID'])

    if _common.present(row_dict, 'Formula'):
        items_api.set_formula(id=row_dict['ID'], body=FormulaUpdateInputV1(
            formula=row_dict['Formula'], parameters=row_dict['Formula Parameters']))


def _needs_sync_token(session: Session, d):
    """
    The sync token allows us to clean up (i.e., archive) items in the
    datasource that have been pushed previously but are no longer desired.
    However, there is a use case where the user pull items that belong to
    an external datasource (e.g., OSIsoft PI), makes a property change
    (like "Maximum Interpolation"), and then pushes them back. In such a
    case, we do not want to modify the sync token because it will have
    adverse effects on the indexing operation by the corresponding
    connector. So we check first to see if this item was pushed from Data
    Lab originally.
    """
    return not _common.present(d, 'ID') or _item_is_from_datalab(session, d['ID'])


def _item_is_from_datalab(session: Session, item_id):
    items_api = ItemsApi(session.client)
    try:
        datasource_class = items_api.get_property(id=item_id, property_name=SeeqNames.Properties.datasource_class).value
        return datasource_class == _common.DEFAULT_DATASOURCE_CLASS
    except ApiException:
        return False


def determine_path(d):
    path = list()
    if _common.present(d, 'Path'):
        path.append(_common.get(d, 'Path'))

    _type = _common.get(d, 'Type')

    if _type != 'Asset' and _common.present(d, 'Asset'):
        path.append(_common.get(d, 'Asset'))

    return _common.path_list_to_string(path)


def get_scoped_data_id(d, workbook_id):
    path = determine_path(d)

    if not _common.present(d, 'Data ID'):
        if path:
            scoped_data_id = '%s >> %s' % (path, d['Name'])
        else:
            scoped_data_id = d['Name']
    else:
        scoped_data_id = d['Data ID']

    if not _is_scoped_data_id(scoped_data_id):
        if not _common.present(d, 'Type'):
            raise SPyRuntimeError('Type is required for all item definitions')

        guid = workbook_id if workbook_id else EMPTY_GUID

        _type = d['Type'].replace('Stored', '').replace('Calculated', '')

        # Need to scope the Data ID to the workbook so it doesn't collide with other workbooks
        scoped_data_id = '[%s] {%s} %s' % (guid, _type, str(scoped_data_id))

    return scoped_data_id.strip()


def _is_scoped_data_id(data_id):
    return re.match(r'^\[%s] {\w+}.*' % _common.GUID_REGEX, data_id) is not None


def _get_unscoped_data_id(scoped_data_id):
    return re.sub(r'^\[%s] {\w+}\s*' % _common.GUID_REGEX, '', scoped_data_id)


def _cleanse_attr(v):
    if isinstance(v, np.generic):
        # Swagger can't handle NumPy types, so we have to retrieve an underlying Python type
        return v.item()
    else:
        return v


def dict_to_input(d, _input, properties_attr, attr_map, capsule_property_units=None):
    lower_case_known_attrs = {k.lower(): k for k in attr_map.keys()}
    for k, v in d.items():
        if k.lower() in lower_case_known_attrs and k not in attr_map:
            raise SPyRuntimeError(f'Incorrect case used for known property: "{k}" should be '
                                  f'"{lower_case_known_attrs[k.lower()]}"')

        if k in attr_map:
            if attr_map[k] is not None:
                v = _common.get(d, k)
                if isinstance(v, list) or not pd.isna(v):
                    setattr(_input, attr_map[k], _cleanse_attr(v))
        elif properties_attr is not None:
            p = ScalarPropertyV1()
            p.name = _common.ensure_unicode(k)

            if p.name in IGNORED_PROPERTIES:
                continue

            uom = None
            if capsule_property_units is not None:
                uom = _common.get(capsule_property_units, p.name.lower())
                if isinstance(v, dict) and uom is not None:
                    raise SPyTypeError(f'Property "{p.name}" cannot have type dict when unit of measure is specified '
                                       f'in metadata')
            if isinstance(v, dict):
                uom = _common.get(v, 'Unit Of Measure')
                v = _common.get(v, 'Value')
            else:
                v = _common.get(d, k)

            if not pd.isna(v):
                if isinstance(v, str) and p.name in ['Cache Enabled', 'Archived', 'Enabled', 'Unsearchable']:
                    # Ensure that these are booleans. Otherwise Seeq Server will silently ignore them.
                    v = (v.lower() == 'true')

                p.value = _cleanse_attr(_common.ensure_unicode(v))

                if uom is not None:
                    p.unit_of_measure = _common.ensure_unicode(uom)
                _properties = getattr(_input, properties_attr)
                if _properties is None:
                    _properties = list()
                _properties.append(p)
                setattr(_input, properties_attr, _properties)

    if _common.present(d, 'UIConfig'):
        ui_config = _common.get(d, 'UIConfig')
        if isinstance(ui_config, dict):
            ui_config = json.dumps(ui_config)
        setattr(_input, '_ui_config', ui_config)


def _set_threshold_levels_from_system(session: Session, threshold_input: ThresholdMetricInputV1):
    """
    Read the threshold limits from the systems endpoint and update the values in the threshold limits. Allows users
    to set thresholds as those defined in the system endpoint such as 'Lo', 'LoLo', 'Hi', 'HiHi', etc.

    :param threshold_input: A Threshold Metric input with a dict in the thresholds with keys of the priority level and
    values of the threshold. Keys are either a numeric value of the threshold, or strings contained in the
    systems/configuration. Values are either scalars or metadata dataframes. If a key is a string that maps to a number
    that is already used in the limits, a RuntimeError will be raised.
    :return: The threshold input with a limits dict with the string values replaced with numbers.
    """
    if not isinstance(threshold_input.thresholds, dict):
        return

    # noinspection PyTypeChecker
    thresholds = threshold_input.thresholds  # type: dict
    threshold_input.thresholds = convert_threshold_levels_from_system(session, thresholds, threshold_input.name)


def convert_threshold_levels_from_system(session: Session, thresholds: dict, item_name) -> dict:
    system_api = SystemApi(session.client)

    # get the priority names and their corresponding levels
    system_settings = system_api.get_server_status()  # type: ServerStatusOutputV1
    priority_levels = {p.name: p.level for p in system_settings.priorities if p.name != 'Neutral'}
    updated_threshold_limits = dict()

    def get_numeric_threshold(threshold):
        # Returns an int representing a threshold priority level
        if isinstance(threshold, int):
            return threshold
        elif isinstance(threshold, str):
            threshold = threshold.split('#')[0].strip()
            if threshold in priority_levels:
                return priority_levels[threshold]
            else:
                try:
                    if int(threshold) in priority_levels.values():
                        return int(threshold)
                    else:
                        raise ValueError
                except ValueError:
                    raise SPyRuntimeError(f'The threshold {threshold} for metric {item_name} is not a valid '
                                          f'threshold level. Valid threshold levels: {list(priority_levels)}')
        else:
            raise SPyRuntimeError(f'The threshold {threshold} is of invalid type {type(threshold)}')

    def get_color_code(threshold):
        # Extracts and returns the color code from a threshold if it exists
        if isinstance(threshold, str):
            parts = threshold.split('#')
            if len(parts) == 2:
                code = parts[1].strip()
                if not re.match(r'^[0-9a-fA-F]{6}$', code):
                    raise SPyRuntimeError(f'"#{code}" is not a valid color hex code')
                return code.lower()
            elif len(parts) > 2:
                raise SPyRuntimeError(f'Threshold "{k}" contains unknown formatting')
        return None

    for k, v in thresholds.items():
        numeric = get_numeric_threshold(k)
        color_code = get_color_code(k)

        if numeric in [get_numeric_threshold(threshold) for threshold in updated_threshold_limits]:
            raise SPyRuntimeError(
                f'Threshold "{k}" maps to a duplicate threshold value for metric {item_name}')

        updated_threshold = '#'.join([str(numeric), color_code]) if color_code is not None else str(numeric)
        updated_threshold_limits[updated_threshold] = v

    return updated_threshold_limits


def dict_to_datasource_input(d, datasource_input):
    dict_to_input(d, datasource_input, None, {
        'Name': 'name',
        'Description': 'description',
        'Datasource Name': 'name',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id'
    })


def dict_to_asset_input(d, asset_input):
    dict_to_input(d, asset_input, 'properties', {
        'Type': None,
        'Name': 'name',
        'Description': 'description',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id',
        'Data ID': 'data_id',
        'Scoped To': 'scoped_to'
    })


def dict_to_signal_input(d, signal_input):
    dict_to_input(d, signal_input, 'additional_properties', {
        'Type': None,
        'Cache ID': None,
        'Name': 'name',
        'Description': 'description',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id',
        'Data ID': 'data_id',
        'Data Version Check': 'data_version_check',
        'Formula': 'formula',
        'Formula Parameters': 'formula_parameters',
        'Interpolation Method': 'interpolation_method',
        'Maximum Interpolation': 'maximum_interpolation',
        'Scoped To': 'scoped_to',
        'Key Unit Of Measure': 'key_unit_of_measure',
        'Value Unit Of Measure': 'value_unit_of_measure',
        'Number Format': 'number_format'
    })


def dict_to_scalar_input(d, scalar_input):
    dict_to_input(d, scalar_input, 'properties', {
        'Type': None,
        'Name': 'name',
        'Description': 'description',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id',
        'Data ID': 'data_id',
        'Data Version Check': 'data_version_check',
        'Formula': 'formula',
        'Formula Parameters': 'parameters',
        'Scoped To': 'scoped_to',
        'Number Format': 'number_format'
    })


def dict_to_condition_input(d, signal_input):
    dict_to_input(d, signal_input, 'properties', {
        'Type': None,
        'Cache ID': None,
        'Name': 'name',
        'Description': 'description',
        'Datasource Class': 'datasource_class',
        'Datasource ID': 'datasource_id',
        'Data ID': 'data_id',
        'Data Version Check': 'data_version_check',
        'Formula': 'formula',
        'Formula Parameters': 'parameters',
        'Maximum Duration': 'maximum_duration',
        'Scoped To': 'scoped_to'
    })


def dict_to_capsule(d, capsule, capsule_property_units=None):
    dict_to_input(d, capsule, 'properties', {
        'Capsule Start': None,
        'Capsule End': None
    }, capsule_property_units=capsule_property_units)


def dict_to_threshold_metric_input(d, metric_input):
    dict_to_input(d, metric_input, 'additional_properties', {
        'Type': None,
        'Name': 'name',
        'Duration': 'duration',
        'Bounding Condition Maximum Duration': 'bounding_condition_maximum_duration',
        'Period': 'period',
        'Thresholds': 'thresholds',
        'Measured Item': 'measured_item',
        'Number Format': 'number_format',
        'Bounding Condition': 'bounding_condition',
        'Metric Neutral Color': 'neutral_color',
        'Scoped To': 'scoped_to',
        'Aggregation Function': 'aggregation_function'
    })


def _handle_reference_uom(session: Session, definition, key):
    if not _common.present(definition, key):
        return

    unit = definition[key]
    if _login.is_valid_unit(session, unit):
        if unit != 'string':
            definition['Formula'] += f".setUnits('{unit}')"
        else:
            definition['Formula'] += f".toString()"
    else:
        # This is the canonical place for unrecognized units
        definition[f'Source {key}'] = unit

    del definition[key]


def _build_reference_signal(session: Session, definition):
    definition['Type'] = 'CalculatedSignal'
    definition['Formula'] = '$signal'

    if _common.present(definition, 'Interpolation Method'):
        definition['Formula'] += f".to{definition['Interpolation Method']}()"
        del definition['Interpolation Method']

    _handle_reference_uom(session, definition, 'Value Unit Of Measure')

    definition['Formula Parameters'] = 'signal=%s' % definition['ID']
    definition['Cache Enabled'] = False

    for key in ['ID', 'Datasource Class', 'Datasource ID', 'Data ID']:
        if _common.present(definition, key) and not _common.present(definition, 'Referenced ' + key):
            definition['Referenced ' + key] = definition[key]
            del definition[key]


def _build_reference_condition(session: Session, definition):
    definition['Type'] = 'CalculatedCondition'
    definition['Formula'] = '$condition'
    definition['Formula Parameters'] = 'condition=%s' % definition['ID']
    definition['Cache Enabled'] = False

    for key in ['ID', 'Datasource Class', 'Datasource ID', 'Data ID', 'Unit Of Measure', 'Maximum Duration']:
        if _common.present(definition, key) and not _common.present(definition, 'Referenced ' + key):
            definition['Referenced ' + key] = definition[key]
            del definition[key]


def _build_reference_scalar(session: Session, definition):
    definition['Type'] = 'CalculatedScalar'
    definition['Formula'] = '$scalar'
    definition['Formula Parameters'] = 'scalar=%s' % definition['ID']
    definition['Cache Enabled'] = False

    _handle_reference_uom(session, definition, 'Unit Of Measure')

    for key in ['ID', 'Datasource Class', 'Datasource ID', 'Data ID']:
        if _common.present(definition, key) and not _common.present(definition, 'Referenced ' + key):
            definition['Referenced ' + key] = definition[key]
            del definition[key]


def build_reference(session: Session, definition):
    {
        'StoredSignal': _build_reference_signal,
        'CalculatedSignal': _build_reference_signal,
        'StoredCondition': _build_reference_condition,
        'CalculatedCondition': _build_reference_condition,
        'CalculatedScalar': _build_reference_scalar
    }[definition['Type']](session, definition)


def _process_formula_parameters(parameters, workbook_id, push_results_df):
    if parameters is None:
        return list()

    if isinstance(parameters, str):
        parameters = [parameters]

    if isinstance(parameters, dict):
        pairs = parameters.items()

    elif isinstance(parameters, list):
        pairs = []
        for param_entry in parameters:
            if not isinstance(param_entry, str):
                raise SPyValueError(f'Formula Parameter entry {param_entry} has invalid type. Must be string.')
            try:
                k, v = param_entry.split('=')
                pairs.append((k, v))
            except ValueError:
                raise SPyValueError(
                    f'Formula Parameter entry "{param_entry}" not recognized. Must be "var=ID" or "var=Path".')

    else:
        raise SPyValueError(f'Formula Parameters have invalid type {type(parameters)}. Valid types are str, list, '
                            f'and dict.')

    processed_parameters = list()
    for k, v in pairs:
        # Strip off leading dollar-sign if it's there
        parameter_name = re.sub(r'^\$', '', k)
        try:
            parameter_id = _item_id_from_parameter_value(v, workbook_id, push_results_df)
        except (ValueError, TypeError) as e:
            raise SPyRuntimeError(f'Error processing {parameter_name}: {e}')
        processed_parameters.append('%s=%s' % (parameter_name, parameter_id))

    processed_parameters.sort(key=lambda param: param.split('=')[0])
    return processed_parameters


def _item_id_from_parameter_value(dict_value, workbook_id, push_results_df):
    if isinstance(dict_value, pd.DataFrame):
        if len(dict_value) == 0:
            raise SPyValueError('The parameter had an empty dataframe')
        if len(dict_value) > 1:
            raise SPyValueError('The parameter had multiple entries in the dataframe')
        dict_value = dict_value.iloc[0]

    def find_id_matching_path(full_path):
        if 'Data ID' in push_results_df:
            # We query Data ID as opposed to Path/Name to ensure that workbook scope
            # is correct and that the dependency has already been pushed
            wb_index = push_results_df['Data ID'].str.startswith('[%s' % workbook_id if workbook_id else EMPTY_GUID,
                                                                 na=False)
            path_index = push_results_df['Data ID'].str.endswith('} %s' % full_path, na=False)
            matching_df = push_results_df[wb_index & path_index]
            if not matching_df.empty and _common.present(matching_df.iloc[0], 'ID'):
                return matching_df.iloc[0]['ID']
            else:
                raise SPyDependencyNotFound(f'Item "{full_path}" was never pushed (error code 4)')
        else:
            raise SPyDependencyNotFound(f'Item "{full_path}" was never pushed (error code 3)')

    if isinstance(dict_value, (dict, pd.Series)):
        if _common.present(dict_value, 'ID') and not _common.get(dict_value, 'Reference', default=False):
            return dict_value['ID']
        elif not _common.present(dict_value, 'Type') and _common.present(dict_value, 'Name'):
            path = _common.path_list_to_string([determine_path(dict_value), dict_value['Name']])
            return find_id_matching_path(path)
        else:
            try:
                scoped_data_id = get_scoped_data_id(dict_value, workbook_id)
            except RuntimeError:
                # This can happen if the dependency didn't get pushed and therefore doesn't have a proper Type
                raise SPyDependencyNotFound(f'Item {dict_value} was never pushed (error code 1)')
            if 'Data ID' in push_results_df:
                pushed_row_i_need = push_results_df[push_results_df['Data ID'] == scoped_data_id]
                if not pushed_row_i_need.empty and _common.present(pushed_row_i_need.iloc[0], 'ID'):
                    return pushed_row_i_need.iloc[0]['ID']
                else:
                    raise SPyDependencyNotFound(f'Item {scoped_data_id} was never pushed (error code 2)')
            else:
                raise SPyDependencyNotFound(f'Item {scoped_data_id} was never pushed (error code 3)')

    elif isinstance(dict_value, str):
        if _common.is_guid(dict_value):
            return dict_value
        # Now treat string like a path
        path = _common.sanitize_path_string(dict_value)
        return find_id_matching_path(path)
    elif dict_value is None:
        raise SPyTypeError('A formula parameter is None, which is not allowed. Check your logic for assigning formula '
                           'parameters and, if you\'re using spy.assets.build(), look for optional Requirements that '
                           'are were not found.')
    else:
        raise SPyTypeError(f'Formula parameter type "{type(dict_value)}" not allowed. Must be DataFrame, Series, '
                           f'dict or ID string')


def _set_push_result_string(dfi, iuo, errors, push_results_df, items_api):
    result_string = 'Success'
    if isinstance(iuo, ItemUpdateOutputV1):
        if iuo.error_message is not None:
            if errors == 'raise':
                raise SPyRuntimeError('Error pushing "%s": %s' % (iuo.data_id, iuo.error_message))
            result_string = iuo.error_message
        else:
            push_results_df.at[dfi, 'Datasource Class'] = iuo.datasource_class
            push_results_df.at[dfi, 'Datasource ID'] = iuo.datasource_id
            push_results_df.at[dfi, 'Data ID'] = iuo.data_id
            push_results_df.at[dfi, 'ID'] = iuo.item.id
            push_results_df.at[dfi, 'Type'] = iuo.item.type
    elif isinstance(iuo, ThresholdMetricOutputV1):
        push_results_df.at[dfi, 'Datasource Class'] = iuo.datasource_class
        push_results_df.at[dfi, 'Datasource ID'] = iuo.datasource_id
        push_results_df.at[dfi, 'Data ID'] = iuo.data_id
        push_results_df.at[dfi, 'ID'] = iuo.id
        push_results_df.at[dfi, 'Type'] = iuo.type
    else:
        raise SPyTypeError('Unrecognized output type from API: %s' % type(iuo))

    row = push_results_df.loc[dfi]
    if not _common.present(row, 'Push Result') or row['Push Result'] == 'Success':
        push_results_df.at[dfi, 'Push Result'] = result_string


def _set_existing_item_push_results(session: Session, index, push_results_df, item_dict, output_object=None):
    if output_object is None:
        if 'Signal' in item_dict['Type']:
            signals_api = SignalsApi(session.client)
            output_object = signals_api.get_signal(id=item_dict['ID'])
        elif 'Scalar' in item_dict['Type']:
            scalars_api = ScalarsApi(session.client)
            output_object = scalars_api.get_scalar(id=item_dict['ID'])
        elif 'Condition' in item_dict['Type']:
            conditions_api = ConditionsApi(session.client)
            output_object = conditions_api.get_condition(id=item_dict['ID'])
        elif 'Metric' in item_dict['Type']:
            metrics_api = MetricsApi(session.client)
            output_object = metrics_api.get_metric(id=item_dict['ID'])
        elif 'Asset' in item_dict['Type']:
            assets_api = AssetsApi(session.client)
            output_object = assets_api.get_asset(id=item_dict['ID'])
    for p in ['ID', 'Type', 'Data ID', 'Datasource Class', 'Datasource ID']:
        attr = p.lower().replace(' ', '_')
        if hasattr(output_object, attr):
            push_results_df.at[index, p] = getattr(output_object, attr)
    push_results_df.at[index, 'Push Result'] = 'Success'


def _process_batch_output(session: Session, item_inputs, item_updates, errors, push_results_df, items_api):
    repost = False
    for i in range(0, len(item_inputs)):
        item_input = item_inputs[i]
        item_update_output = item_updates[i]  # type: ItemUpdateOutputV1

        if item_update_output.error_message and \
                SeeqNames.API.ErrorMessages.attempted_to_set_scope_on_a_globally_scoped_item in \
                item_update_output.error_message:
            # This handles CRAB-25450. Metadata that was posted prior to that bugfix may have a non-fixable
            # global-scope applied, so rather than error out, just repost with global-scope. This effectively
            # preserves status quo for those users.
            setattr(item_input, 'scoped_to', None)
            repost = True
            continue

        if not isinstance(item_input, AssetInputV1):
            _push_ui_config(session, item_input, item_update_output.item)

        if hasattr(item_input, 'dataframe_index'):
            _set_push_result_string(item_input.dataframe_index, item_update_output, errors, push_results_df, items_api)

    return repost


def _post_batch(session: Session, post_function, item_inputs, errors, push_results_df, items_api):
    item_batch_output = post_function()
    repost = _process_batch_output(session, item_inputs, item_batch_output.item_updates, errors, push_results_df,
                                   items_api)
    if repost:
        # This means we're supposed to repost the batch because _process_batch_output() has modified the scoped_to
        # property on some items to overcome CRAB-25450. See test_metadata.test_crab_25450().
        item_batch_output = post_function()
        _process_batch_output(session, item_inputs, item_batch_output.item_updates, errors, push_results_df, items_api)


def _flush(session: Session, put_signals_input, put_scalars_input, condition_batch_input, threshold_metric_inputs,
           asset_batch_input, tree_batch_input, push_results_df, errors):
    items_api = ItemsApi(session.client)
    signals_api = SignalsApi(session.client)
    scalars_api = ScalarsApi(session.client)
    conditions_api = ConditionsApi(session.client)
    assets_api = AssetsApi(session.client)
    trees_api = TreesApi(session.client)
    metrics_api = MetricsApi(session.client)

    if len(put_signals_input.signals) > 0:
        _post_batch(session, lambda: signals_api.put_signals(body=put_signals_input), put_signals_input.signals,
                    errors, push_results_df, items_api)
        put_signals_input.signals = list()

    if len(put_scalars_input.scalars) > 0:
        _post_batch(session, lambda: scalars_api.put_scalars(body=put_scalars_input), put_scalars_input.scalars,
                    errors, push_results_df, items_api)
        put_scalars_input.scalars = list()

    if len(condition_batch_input.conditions) > 0:
        _post_batch(session, lambda: conditions_api.put_conditions(body=condition_batch_input),
                    condition_batch_input.conditions, errors, push_results_df, items_api)
        condition_batch_input.conditions = list()

    if len(threshold_metric_inputs) > 0:
        for tm in threshold_metric_inputs:
            # Check if the metric already exists
            metric_search = items_api.search_items(
                filters=[f'Datasource Class == {tm.datasource_class} '
                         f'&& Datasource ID == {tm.datasource_id} '
                         f'&& Data ID == {tm.data_id}',
                         '@includeUnsearchable'])
            if metric_search.total_results > 1:
                raise SPyRuntimeError('More than one metric had the data triplet {}, {}, {}'.format(tm.datasource_class,
                                                                                                    tm.datasource_id,
                                                                                                    tm.data_id))
            if metric_search.total_results == 1:
                tm_output = metrics_api.get_metric(id=metric_search.items[0].id)
                if tm_output.scoped_to is None and tm.scoped_to is not None:
                    # This handles CRAB-25450
                    tm.scoped_to = None

                # Workaround for CRAB-29202: Explicitly un-archive the metric using Additional Properties
                if tm.additional_properties is None:
                    tm.additional_properties = list()
                if all((prop.name != 'Archived' for prop in tm.additional_properties)):
                    tm.additional_properties.append(ScalarPropertyV1(name='Archived', value=False))

                tm_push_output = metrics_api.put_threshold_metric(id=metric_search.items[0].id,
                                                                  body=tm)
            else:
                tm_push_output = metrics_api.create_threshold_metric(body=tm)
                _add_data_properties(session, tm_push_output, tm.datasource_class, tm.datasource_id, tm.data_id)

            _set_push_result_string(tm.dataframe_index, tm_push_output, errors, push_results_df, items_api)

        threshold_metric_inputs.clear()

    if len(asset_batch_input.assets) > 0:
        _post_batch(session, lambda: assets_api.batch_create_assets(body=asset_batch_input), asset_batch_input.assets,
                    errors, push_results_df, items_api)
        asset_batch_input.assets = list()

    if len(tree_batch_input.relationships) > 0:
        _post_batch(session, lambda: trees_api.batch_move_nodes_to_parents(body=tree_batch_input),
                    tree_batch_input.relationships, errors, push_results_df, items_api)  # type: ItemBatchOutputV1
        tree_batch_input.relationships = list()


def _add_data_properties(session: Session, item, datasource_class, datasource_id, data_id):
    """
    Add a property with a Data ID for items that do not take a data id in their input

    :param item: The output of item creation containing the item's seeq ID
    :param datasource_class: The datasource class to apply to the item
    :param datasource_id: The datasource id to apply to the item
    :param data_id: The data id to add to the item
    :return:
    """
    items_api = ItemsApi(session.client)
    properties_input = [
        ScalarPropertyV1(unit_of_measure='string', name='Datasource Class', value=datasource_class),
        ScalarPropertyV1(unit_of_measure='string', name='Datasource ID', value=datasource_id),
        ScalarPropertyV1(unit_of_measure='string', name='Data ID', value=data_id)
    ]
    items_api.set_properties(id=item.id, body=properties_input)


def _convert_thresholds_dict_to_input(thresholds_dict, workbook_id, push_results_df):
    """
    Convert a dictionary with keys threshold levels and values of either scalars or metadata to a list of strings
    with level=value/ID of the threshold.

    :param thresholds_dict: A dictionary with keys of threshold levels and values of either number of metadata
    dataframes
    :return:  A list of strings 'level=value' or 'level=ID'
    """

    thresholds_list = list()
    if thresholds_dict:
        for k, v in thresholds_dict.items():
            if isinstance(v, pd.DataFrame) or isinstance(v, dict):
                thresholds_list.append(
                    f'{k}={_item_id_from_parameter_value(v, workbook_id, push_results_df)}')
            else:
                thresholds_list.append(f'{k}={v}')
    return thresholds_list


def _add_no_dupe(lst, obj, attr='data_id', overwrite=False):
    for i in range(0, len(lst)):
        o = lst[i]
        if hasattr(o, attr):
            if getattr(o, attr) == getattr(obj, attr):
                if overwrite:
                    lst[i] = obj
                return 0

    lst.append(obj)
    return 1


def _is_handled_type(type_value):
    try:
        return 'Signal' in type_value \
               or 'Scalar' in type_value \
               or 'Condition' in type_value \
               or 'Metric' in type_value \
               or type_value == 'Asset'
    except TypeError:
        return False


def _reify_path(path, workbook_id, datasource_output, scoped_data_id, cache, roots, asset_batch_input,
                tree_batch_input, sync_token, status, index):
    path_items = _common.path_string_to_list(path)

    root_data_id = get_scoped_data_id({
        'Name': '',
        'Type': 'Asset'
    }, workbook_id)

    path_so_far = list()

    parent_data_id = root_data_id
    child_data_id = root_data_id
    for path_item in path_items:
        if len(path_item) == 0:
            raise SPyValueError('Path contains blank / zero-length segments: "%s"' % path)

        asset_input = AssetInputV1()
        asset_input.name = path_item
        asset_input.scoped_to = workbook_id
        asset_input.host_id = datasource_output.id
        asset_input.sync_token = sync_token

        tree_input = AssetTreeSingleInputV1()
        tree_input.parent_data_id = parent_data_id

        path_so_far.append(path_item)

        child_data_id = get_scoped_data_id({
            'Name': path_so_far[-1],
            'Path': _common.path_list_to_string(path_so_far[0:-1]),
            'Type': 'Asset'
        }, workbook_id)

        asset_input.data_id = child_data_id
        tree_input.child_data_id = child_data_id

        if asset_input.data_id not in cache:
            if tree_input.parent_data_id != root_data_id:
                status.df['Relationship'] += 1
                setattr(tree_input, 'dataframe_index', index)
                tree_batch_input.relationships.append(tree_input)
            else:
                roots[asset_input.data_id] = asset_input

            setattr(asset_input, 'dataframe_index', index)
            status.df['Asset'] += _add_no_dupe(asset_batch_input.assets, asset_input)

            cache[asset_input.data_id] = True

        parent_data_id = child_data_id

    tree_input = AssetTreeSingleInputV1()
    tree_input.parent_data_id = child_data_id
    tree_input.child_data_id = scoped_data_id
    setattr(tree_input, 'dataframe_index', index)
    status.df['Relationship'] += _add_no_dupe(tree_batch_input.relationships, tree_input, 'child_data_id')


def create_datasource(session: Session, datasource=None):
    items_api = ItemsApi(session.client)
    datasources_api = DatasourcesApi(session.client)
    users_api = UsersApi(session.client)

    datasource_input = _common.get_data_lab_datasource_input()
    if datasource is not None:
        if not isinstance(datasource, (str, dict)):
            raise SPyValueError('"datasource" parameter must be str or dict')

        if isinstance(datasource, str):
            datasource_input.name = datasource
            datasource_input.datasource_id = datasource_input.name
        else:
            if 'Datasource Name' not in datasource:
                raise SPyValueError(
                    '"Datasource Name" required for datasource. This is the specific data set being pushed. '
                    'For example, "Permian Basin Well Data"')

            if 'Datasource Class' in datasource:
                raise SPyValueError(
                    '"Datasource Class" cannot be specified for datasource. It will always be '
                    f'"{_common.DEFAULT_DATASOURCE_CLASS}".')

            dict_to_datasource_input(datasource, datasource_input)

        if datasource_input.datasource_id == _common.DEFAULT_DATASOURCE_ID:
            datasource_input.datasource_id = datasource_input.name

    datasource_output_list = datasources_api.get_datasources(datasource_class=datasource_input.datasource_class,
                                                             datasource_id=datasource_input.datasource_id,
                                                             limit=2)  # type: DatasourceOutputListV1

    if len(datasource_output_list.datasources) > 1:
        raise SPyRuntimeError(f'Multiple datasources found with class {datasource_input.datasource_class} '
                              f'and ID {datasource_input.datasource_id}')

    if len(datasource_output_list.datasources) == 1:
        return datasource_output_list.datasources[0]

    datasource_output = datasources_api.create_datasource(body=datasource_input)  # type: DatasourceOutputV1

    # Due to CRAB-23806, we have to immediately call get_datasource to get the right set of additional properties
    datasource_output = datasources_api.get_datasource(id=datasource_output.id)

    # We need to add Everyone with Manage permissions so that all users can push asset trees
    identity_preview_list = users_api.autocomplete_users_and_groups(query='Everyone')  # type: IdentityPreviewListV1
    everyone_user_group_id = None
    for identity_preview in identity_preview_list.items:  # type: IdentityPreviewV1
        if identity_preview.type == 'UserGroup' and \
                identity_preview.name == 'Everyone' and \
                identity_preview.datasource.name == 'Seeq' and \
                identity_preview.is_enabled:
            everyone_user_group_id = identity_preview.id
            break

    if everyone_user_group_id:
        items_api.add_access_control_entry(id=datasource_output.id, body=AceInputV1(
            identity_id=everyone_user_group_id,
            permissions=PermissionsV1(manage=True, read=True, write=True)
        ))

    return datasource_output


def push_access_control(session: Session, item_id: str, acl_df: pd.DataFrame, replace: bool,
                        disable_permission_inheritance: Optional[bool] = None):
    items_api = ItemsApi(session.client)
    acl_output: AclOutputV1 = items_api.get_access_control(id=item_id)

    if disable_permission_inheritance is None:
        # None means "don't change it"
        disable_permission_inheritance = acl_output.permissions_inheritance_disabled

    if disable_permission_inheritance != acl_output.permissions_inheritance_disabled:
        items_api.set_acl_inheritance(id=item_id, inherit_acl=not disable_permission_inheritance)
        acl_output = items_api.get_access_control(id=item_id)

    ace_inputs = list()
    for _, ace_to_push in acl_df.iterrows():
        found = False

        # We sort so that the system-managed entries are found first, and item-specific entries will be removed
        # if they're already covered by the system-managed entries
        sorted_acl_entries = sorted(acl_output.entries, key=lambda e: e.role != 'OWNER' and e.origin is None)
        for existing_ace in sorted_acl_entries:  # type: AceOutputV1
            if (existing_ace.identity.id == ace_to_push['ID'] and
                    existing_ace.permissions.read == ace_to_push['Read'] and
                    existing_ace.permissions.write == ace_to_push['Write'] and
                    existing_ace.permissions.manage == ace_to_push['Manage']):
                found = True
                setattr(existing_ace, 'used', True)
                break

        if found:
            continue

        permissions = PermissionsV1(read=ace_to_push['Read'], write=ace_to_push['Write'], manage=ace_to_push['Manage'])
        ace_inputs.append((permissions, ace_to_push['ID']))

    if replace:
        # It's important to remove the entries that need to be removed before adding. Otherwise, if you try to
        # add an ACE that conflicts with an existing entry, it will be silently ignored.
        for existing_ace in acl_output.entries:  # type: AceOutputV1
            if existing_ace.role == 'OWNER' or (not disable_permission_inheritance and existing_ace.origin is not None):
                # You can't remove OWNER or inherited permissions
                continue

            if hasattr(existing_ace, 'used') and getattr(existing_ace, 'used'):
                continue

            items_api.remove_access_control_entry(id=item_id, ace_id=existing_ace.id)

    for permissions, identity_id in ace_inputs:
        items_api.add_access_control_entry(id=item_id,
                                           body=AceInputV1(permissions=permissions,
                                                           identity_id=identity_id))


def dict_from_scalar_value_output(scalar_value_output):
    """
    :type scalar_value_output: ScalarValueOutputV1
    """
    d = dict()
    d['Value'] = scalar_value_output.value
    d['Unit Of Measure'] = scalar_value_output.uom
    return d


def str_from_scalar_value_dict(scalar_value_dict):
    if isinstance(scalar_value_dict['Value'], str):
        return '%s' % scalar_value_dict['Value']
    elif isinstance(scalar_value_dict['Value'], int):
        return '%d %s' % (scalar_value_dict['Value'], scalar_value_dict['Unit Of Measure'])
    else:
        return '%f %s' % (scalar_value_dict['Value'], scalar_value_dict['Unit Of Measure'])


def formula_parameters_dict_from_threshold_metric(session: Session, item_id):
    metrics_api = MetricsApi(session.client)
    metric = metrics_api.get_metric(id=item_id)  # type: ThresholdMetricOutputV1
    formula_parameters = dict()
    if metric.aggregation_function is not None:
        formula_parameters['Aggregation Function'] = metric.aggregation_function
    if metric.bounding_condition is not None:
        formula_parameters['Bounding Condition'] = metric.bounding_condition.id
    if metric.bounding_condition_maximum_duration is not None:
        formula_parameters['Bounding Condition Maximum Duration'] = \
            dict_from_scalar_value_output(metric.bounding_condition_maximum_duration)
    if metric.duration is not None:
        formula_parameters['Duration'] = dict_from_scalar_value_output(metric.duration)
    if metric.measured_item is not None:
        formula_parameters['Measured Item'] = metric.measured_item.id
    if hasattr(metric, 'number_format') and metric.number_format is not None:
        formula_parameters['Number Format'] = metric.number_format
    if metric.period is not None:
        formula_parameters['Period'] = dict_from_scalar_value_output(metric.period)
    if metric.process_type is not None:
        formula_parameters['Process Type'] = metric.process_type

    def _add_thresholds(_thresholds_name, _threshold_output_list):
        formula_parameters[_thresholds_name] = list()
        for threshold in _threshold_output_list:  # type: ThresholdOutputV1
            threshold_dict = dict()
            if threshold.priority is not None:
                priority = threshold.priority  # type: PriorityV1
                threshold_dict['Priority'] = {
                    'Name': priority.name,
                    'Level': priority.level,
                    'Color': priority.color
                }

            if not threshold.is_generated and threshold.item:
                threshold_dict['Item ID'] = threshold.item.id

            if threshold.value is not None:
                if isinstance(threshold.value, ScalarValueOutputV1):
                    threshold_dict['Value'] = dict_from_scalar_value_output(threshold.value)
                else:
                    threshold_dict['Value'] = threshold.value

            formula_parameters[_thresholds_name].append(threshold_dict)

    if metric.thresholds:
        _add_thresholds('Thresholds', metric.thresholds)

    return formula_parameters


def threshold_metric_input_from_formula_parameters(parameters, *, item_object=None,
                                                   item_map=None) -> ThresholdMetricInputV1:
    new_item = ThresholdMetricInputV1()

    def _add_scalar_value(_attr, _key):
        if _common.present(parameters, _key):
            setattr(new_item, _attr, str_from_scalar_value_dict(parameters[_key]))

    def _add_mapped_item(_attr, _key):
        if _common.present(parameters, _key):
            if item_map is None:
                setattr(new_item, _attr, parameters[_key].upper())
                return

            if parameters[_key] not in item_map:
                raise SPyDependencyNotFound(
                    f'{item_object} Threshold Metric parameter {_key} ({parameters[_key]}) not found')

            setattr(new_item, _attr, item_map[parameters[_key].upper()])

    def _add_thresholds(_list, _key):
        if not _common.present(parameters, _key):
            return

        for threshold_dict in parameters[_key]:
            threshold_value = _common.get(threshold_dict, 'Value')
            if threshold_value is not None:
                if isinstance(threshold_value, dict):
                    _list.append('%s=%s' % (threshold_dict['Priority']['Level'],
                                            str_from_scalar_value_dict(threshold_value)))
                else:
                    _list.append('%s=%s' % (threshold_dict['Priority']['Level'], threshold_value))
            elif _common.present(threshold_dict, 'Item ID'):
                if item_map is None:
                    _list.append('%s=%s' % (threshold_dict['Priority']['Level'], threshold_dict['Item ID'].upper()))
                    return

                if threshold_dict['Item ID'] not in item_map:
                    raise SPyDependencyNotFound(
                        f'{item_object} Threshold Metric threshold {threshold_dict["Item ID"]}) not found')

                _list.append('%s=%s' % (threshold_dict['Priority']['Level'],
                                        item_map[threshold_dict['Item ID'].upper()]))

    new_item.aggregation_function = _common.get(parameters, 'Aggregation Function')
    _add_mapped_item('bounding_condition', 'Bounding Condition')
    _add_scalar_value('bounding_condition_maximum_duration', 'Bounding Condition Maximum Duration')
    _add_scalar_value('duration', 'Duration')
    _add_mapped_item('measured_item', 'Measured Item')
    _add_scalar_value('period', 'Period')
    new_item.thresholds = list()
    _add_thresholds(new_item.thresholds, 'Thresholds')

    return new_item


RESERVED_SPY_STATUS_COLUMN_NAMES = [
    'Push Result', 'Push Count', 'Push Time',
    'Pull Result', 'Pull Count', 'Pull Time',
    'Build Result'
]

RESERVED_SPY_COLUMN_NAMES = [
                                'Build Path', 'Build Asset', 'Build Template',
                                'ID', 'Type', 'Path', 'Asset', 'Object', 'Asset Object', 'Depth',
                                'Formula Parameters', 'Capsule Is Uncertain', 'Capsule Property Units',
                                'Override Number Format', 'Condition',
                                'Permissions Inheritance Disabled', 'Access Control',
                                'Roll Up Statistic', 'Roll Up Parameters',
                            ] + RESERVED_SPY_STATUS_COLUMN_NAMES

# This must be kept in sync with RESERVED_ITEM_PROPERTIES in StoredItemOutput.java
RESERVED_ITEM_PROPERTIES = [
    SeeqNames.Properties.guid,
    SeeqNames.Properties.datasource_class,
    SeeqNames.Properties.datasource_id,
    SeeqNames.Properties.data_id,
    SeeqNames.Properties.name,
    SeeqNames.Properties.description,
    SeeqNames.Properties.interpolation_method,
    SeeqNames.Properties.maximum_duration,
    SeeqNames.Properties.maximum_interpolation,
    SeeqNames.Properties.source_maximum_interpolation,
    SeeqNames.Properties.override_maximum_interpolation,
    SeeqNames.Properties.key_uom,
    SeeqNames.Properties.value_uom,
    SeeqNames.Properties.uom,
    SeeqNames.Properties.number_format,
    SeeqNames.Properties.source_number_format,
    SeeqNames.Properties.formula,
    SeeqNames.Properties.formula_parameters,
    SeeqNames.Properties.u_i_config,
    SeeqNames.Properties.data_version_check,
    SeeqNames.Properties.sync_token,
    SeeqNames.Properties.permissions_from_datasource,
    SeeqNames.Properties.source_security_string,
    SeeqNames.Properties.security_string,
    SeeqNames.Properties.cache_id,
    SeeqNames.Properties.cached_by_service
]

ADDITIONAL_RESERVED_PROPERTIES = [SeeqNames.Properties.scoped_to, SeeqNames.Properties.metadata_properties,
                                  SeeqNames.Properties.storage_location, SeeqNames.Properties.stored_in_seeq]

IGNORED_PROPERTIES = RESERVED_SPY_COLUMN_NAMES + RESERVED_ITEM_PROPERTIES + ADDITIONAL_RESERVED_PROPERTIES
