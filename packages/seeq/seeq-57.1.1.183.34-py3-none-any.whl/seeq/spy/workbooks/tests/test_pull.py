import os
import tempfile
from unittest import mock

import pytest

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common
from seeq.spy._errors import SPyRuntimeError
from seeq.spy.tests import test_common
from seeq.spy.workbooks import Workbook, Topic
from seeq.spy.workbooks._content import DateRange
from seeq.spy.workbooks.tests import test_load


def setup_module():
    test_common.initialize_sessions()


def _push_example_export(label):
    example_export_push_df = spy.workbooks.push(
        test_load.load_example_export(), refresh=False, path=label, label=label)
    example_export_push_df.drop(columns=['ID'], inplace=True)
    example_export_push_df.rename(columns={'Pushed Workbook ID': 'ID'}, inplace=True)
    example_export_push_df['Type'] = 'Workbook'
    return example_export_push_df


# The tests for pulling workbooks are light because so much of the functionality is tested in the push code. I.e.,
# the push code wouldn't work if the pull code had a problem, since the pull code is what produced the saved workbooks.
# (Same goes for the spy.workbooks.save() functionality.)

@pytest.mark.system
def test_pull():
    example_export_push_df = _push_example_export('test_pull')

    # Make sure the "include_references" functionality works properly by just specifying the Topic. It'll pull in
    # the Analyses
    to_pull_df = example_export_push_df[example_export_push_df['Workbook Type'] == 'Topic'].copy()

    pull_workbooks = spy.workbooks.pull(to_pull_df)

    pull_workbooks = sorted(pull_workbooks, key=lambda w: w['Workbook Type'])

    analysis = pull_workbooks[0]  # type: Workbook
    assert analysis.id == (example_export_push_df[
        example_export_push_df['Workbook Type'] == 'Analysis'].iloc[0]['ID'])
    assert analysis.name == (example_export_push_df[
        example_export_push_df['Workbook Type'] == 'Analysis'].iloc[0]['Name'])
    assert len(analysis.datasource_maps) >= 3
    assert len(analysis.item_inventory) >= 25

    assert analysis['URL'] == example_export_push_df[
        example_export_push_df['Workbook Type'] == 'Analysis'].iloc[0]['URL']

    worksheet_names = [w.name for w in analysis.worksheets]
    assert worksheet_names == [
        'Details Pane',
        'Calculated Items',
        'Histogram',
        'Metrics',
        'Journal',
        'Global',
        'Boundaries'
    ]

    topic = pull_workbooks[1]
    worksheet_names = [w.name for w in topic.worksheets]
    assert len(topic.datasource_maps) == 2
    assert worksheet_names == [
        'Static Doc',
        'Live Doc'
    ]

    # Pull specific worksheets
    to_pull_df = example_export_push_df[example_export_push_df['Workbook Type'] == 'Analysis'].copy()
    specific_worksheet_ids = {ws.id for ws in analysis.worksheets if ws.name in ['Metrics', 'Journal']}
    pull_workbooks = spy.workbooks.pull(to_pull_df, specific_worksheet_ids=list(specific_worksheet_ids))

    assert len(pull_workbooks) == 1
    assert len(pull_workbooks[0].worksheets) == 2
    worksheet_ids = {ws.id for ws in pull_workbooks[0].worksheets}
    assert worksheet_ids == specific_worksheet_ids


@pytest.mark.system
def test_render():
    _push_example_export('test_render')

    search_df = spy.workbooks.search({
        'Workbook Type': 'Topic',
        'Path': 'test_render',
        'Name': 'Example Topic'
    }, recursive=True)

    spy.options.clear_content_cache_before_render = True

    workbooks = spy.workbooks.pull(search_df, include_rendered_content=True, include_referenced_workbooks=False,
                                   include_inventory=False)

    with tempfile.TemporaryDirectory() as temp:
        spy.workbooks.save(workbooks, temp, include_rendered_content=True)
        topic = [w for w in workbooks if isinstance(w, Topic)][0]

        topic_folder = os.path.join(temp, f'Example Topic ({topic.id})')
        assert os.path.exists(topic_folder)

        render_folder = os.path.join(topic_folder, 'RenderedTopic')
        assert os.path.exists(os.path.join(render_folder, 'index.html'))
        for worksheet in topic.worksheets:
            assert os.path.exists(os.path.join(render_folder, f'{worksheet.document.id}.html'))
            for content_image in worksheet.document.rendered_content_images.keys():
                assert os.path.exists(_common.get_image_file(render_folder, content_image))

            for static_image in worksheet.document.images.keys():
                assert os.path.exists(_common.get_image_file(render_folder, static_image))


@pytest.mark.system
def test_pull_static_date_range_with_comments():
    # Create a topic document with a static date range (no content necessary)
    topic = Topic('test_pull_static_date_range_with_comments')
    doc = topic.document('CRAB_22740')
    date_range = DateRange({
        'Name': 'A Static Date Range!',
        'Start': '2020-12-17T00:00:00Z',
        'End': '2020-12-18T00:00:00Z',
    }, doc.document)
    doc.date_ranges[date_range.id] = date_range

    # Since we use the default value for refresh (True), all of the identifiers for all of the in-memory Python objects
    # will be updated such that their IDs are correct, and we can just use date_range.id below.
    spy.workbooks.push(topic)

    content_api = ContentApi(spy.session.client)
    date_range_output = content_api.get_date_range(id=date_range.id)

    # Add a comment to the formula, just like the Seeq Workbench frontend would do.
    content_api.update_date_range(id=date_range.id, body=DateRangeInputV1(
        name=date_range_output.name,
        report_id=date_range_output.report.id,
        formula='// This is a comment!\n' + date_range_output.formula
    ))

    # Pull a date range. Should contains Start and End properties
    pulled_data_range = date_range.pull(date_range.id)
    assert 'Start' in pulled_data_range
    assert 'End' in pulled_data_range

    # Add a comment to the end of the formula
    content_api.update_date_range(id=date_range.id, body=DateRangeInputV1(
        name=date_range_output.name,
        report_id=date_range_output.report.id,
        formula='//A comment \n' + date_range_output.formula + '// and one more comment!'
    ))

    pulled_data_range = date_range.pull(date_range.id)
    assert 'Start' in pulled_data_range
    assert 'End' in pulled_data_range


@pytest.mark.system
def test_pull_url():
    topic = Topic('test_pull_url')
    topic.document('test_pull_url_worksheet')
    push_result = spy.workbooks.push(topic)
    url = push_result['URL'][0]

    # Pull the pushed workbook by URL
    workbooks = spy.workbooks.pull(url)
    assert len(workbooks) == 1
    pulled_topic = workbooks[0]
    assert pulled_topic['Name'] == 'test_pull_url'
    assert pulled_topic['Workbook Type'] == 'Topic'


@pytest.mark.system
def test_redacted_pull():
    workbooks = test_load.load_example_export()

    path = f'Pull Folder Redaction {_common.new_placeholder_guid()}'
    spy.workbooks.push(workbooks, path=path, label=path, errors='catalog')
    search_df = spy.workbooks.search({'Path': path})
    assert len(search_df) >= 1
    reason = 'No thanks'
    mock_exception_thrower = mock.Mock(side_effect=ApiException(status=403, reason=reason))

    def _pull_and_assert_redaction_individual_items(expected_warning):
        with pytest.raises(ApiException, match=reason):
            spy.workbooks.pull(search_df, include_rendered_content=True)

        _status = spy.Status()
        _pull_results = spy.workbooks.pull(search_df, include_rendered_content=True, errors='catalog', status=_status)
        assert len(_pull_results) >= 1
        assert len(_status.warnings) >= 1, f'No warnings found in status {_status}'
        warning_matches = [w for w in _status.warnings if expected_warning in w]
        assert warning_matches, f'Expected warning "{expected_warning}" not found in {_status.warnings}'

    def _pull_and_assert_redaction_scraped_items():
        with pytest.raises(SPyRuntimeError):
            spy.workbooks.pull(search_df)
        # Scraped items go through a more complex workflow where the errors accumulate in item_pull_errors,
        # which outputs as a single unified warning
        _status = spy.Status()
        _pull_results = spy.workbooks.pull(search_df, errors='catalog', status=_status)
        assert len(_pull_results) >= 1
        assert len(_status.warnings) >= 1, f'No warnings found in status {_status}'
        warning_matches = [w for w in _status.warnings if reason in w]
        assert warning_matches, f'Expected warning "{reason}" not found in {_status.warnings}'

    with mock.patch('seeq.sdk.ItemsApi.get_access_control', new=mock_exception_thrower):
        _pull_and_assert_redaction_individual_items('Failed to get access control list for Item')

    with mock.patch('seeq.sdk.ContentApi.get_contents_with_all_metadata', new=mock_exception_thrower):
        _pull_and_assert_redaction_individual_items('Failed to get Content items within Report')

    with mock.patch('seeq.sdk.WorkbooksApi.get_workbook', new=mock_exception_thrower):
        _pull_and_assert_redaction_individual_items('Failed to get details for Workbook')

    with mock.patch('seeq.sdk.WorkbooksApi.get_worksheets', new=mock_exception_thrower):
        _pull_and_assert_redaction_individual_items('Failed to gather all Worksheets within Workbook')

    with mock.patch('seeq.sdk.WorkbooksApi.get_worksheet', new=mock_exception_thrower):
        _pull_and_assert_redaction_individual_items('Failed to get Worksheet details for')

    with mock.patch('seeq.sdk.WorkbooksApi.get_workstep', new=mock_exception_thrower):
        _pull_and_assert_redaction_individual_items('Failed to get Workstep details at')

    with mock.patch('seeq.sdk.UsersApi.get_user', new=mock_exception_thrower):
        _pull_and_assert_redaction_individual_items('Failed to get User')

    # Catching errors while scraping workbook inventory is higher-level so it has slightly different expected behavior
    with mock.patch('seeq.sdk.SignalsApi.get_signal', new=mock_exception_thrower):
        _pull_and_assert_redaction_scraped_items()

    with mock.patch('seeq.sdk.ConditionsApi.get_condition', new=mock_exception_thrower):
        _pull_and_assert_redaction_scraped_items()

    with mock.patch('seeq.sdk.ScalarsApi.get_scalar', new=mock_exception_thrower):
        _pull_and_assert_redaction_scraped_items()
