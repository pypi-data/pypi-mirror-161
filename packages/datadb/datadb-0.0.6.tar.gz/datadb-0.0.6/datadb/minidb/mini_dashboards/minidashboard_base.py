import pandas as pd
from bokeh.layouts import row, column
from bokeh.models.widgets import Div
from pandas.core.dtypes.common import is_datetime64_any_dtype, is_numeric_dtype, is_string_dtype

from datadb.minidb.building_blocks.base.boxplot import boxplot
from datadb.minidb.building_blocks.base.describe_table import descriptiontable
from datadb.minidb.building_blocks.base.histogram import histogram
from datadb.minidb.building_blocks.base.value_counts_table import valuecountstable


def minidashboard_base(df: pd.core.frame.DataFrame,
                       attr):


    sr = df[attr].copy(deep=True)

    description_table = descriptiontable(sr)




    if is_numeric_dtype(sr) or is_datetime64_any_dtype(sr):
        n_unique = len(sr.unique())
        if n_unique < 20:
            sr = sr.astype(str)


    if is_numeric_dtype(sr) or is_datetime64_any_dtype(sr):
        hist = histogram(sr)
        box = boxplot(sr)
        layout = row(description_table, hist, box)


    elif is_string_dtype(sr):

        value_counts = sr.value_counts(dropna=False) \
            .reset_index() \
            .rename(columns={'index': 'value',
                             sr.name: 'counts'})
        N = len(sr)
        value_counts['perc'] = (value_counts.counts / N).map('{:.2%}'.format)
        value_counts_table = valuecountstable(value_counts)


        layout = row(description_table, value_counts_table)


    db_title = Div(text=""" <b> ==============================================  UNIVARIATE  ============================================== </b>
              """,
                   width=800, height=20)
    layout = column(db_title, layout)

    return layout


