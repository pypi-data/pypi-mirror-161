from __future__ import annotations

import pandas as pd

reference_types = ['StoredSignal', 'StoredCondition']
calculated_types = ['CalculatedScalar', 'CalculatedSignal', 'CalculatedCondition']
metric_types = ['Metric', 'ThresholdMetric']
data_types = calculated_types + reference_types
supported_input_types = data_types + metric_types + ['Asset']
supported_output_types = calculated_types + ['Asset']

dataframe_dtypes = {
    'ID': str,
    'Referenced ID': str,
    'Path': str,
    'Name': str,
    'Type': str,
    'Depth': int,
    'Description': str,
    'Formula': str,
    'Formula Parameters': (str, list, dict, pd.Series, pd.DataFrame),
    'Roll Up Statistic': str,
    'Roll Up Parameters': str,
    # Below are metric-specific columns
    'Aggregation Function': str,
    'Statistic': str,  # 'Statistic' is the friendly SPy input for 'Aggregation Function'
    'Bounding Condition': (str, dict),
    'Bounding Condition Maximum Duration': str,
    'Duration': str,
    'Number Format': str,
    'Measured Item': (str, dict),
    'Metric Neutral Color': str,
    'Period': str,
    'Process Type': str,
    'Thresholds': (dict, list)
}
dataframe_columns = list(dataframe_dtypes.keys())

MAX_ERRORS_DISPLAYED = 3
MAX_FORMULA_DEPENDENCY_DEPTH = 1000
