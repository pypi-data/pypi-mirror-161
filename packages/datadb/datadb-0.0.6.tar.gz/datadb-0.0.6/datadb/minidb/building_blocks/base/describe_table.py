import math
import pandas as pd
from bokeh.layouts import column

from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, Div


def descriptiontable(sr):
    n_digits = 5

    def round_to_n_digits(x):
        return round(x, n_digits - int(math.floor(math.log10(abs(x)))) - 1) if x else x

    def my_round(x):
        return round(x) if abs(x) > (10 ** (n_digits - 1)) else round_to_n_digits(x)

    def my_format(x):
        return f"{my_round(x):,}"


    type_ = sr.dtypes

    n = len(sr)
    n_null = sum(sr.isnull())
    pct_null = f'{n_null / n:.1%}'

    n = my_format(n)
    n_null = my_format(n_null)

    # TO DO: add support for datetime
    if type_ in ['float32', 'float64', '<M8[ns]', 'int64']:
        min_ = sr.min()
        max_ = sr.max()
        mean_ = sr.mean()

        if type_ == '<M8[ns]':
            min_ = min_.strftime('%Y-%m-%d')
            max_ = max_.strftime('%Y-%m-%d')
            mean_ = mean_.strftime('%Y-%m-%d')
        else:
            min_ = my_format(min_)
            max_ = my_format(max_)
            mean_ = my_format(mean_)

        desc_table = pd.DataFrame([['N', n],
                                   ['N_null', n_null],
                                   ['pct_null', pct_null],
                                   ['min', min_],
                                   ['max', max_],
                                   ['mean', mean_]], columns=['Metric', 'Value'])
    else:
        n_unique = len(sr.unique())
        n_unique = my_format(n_unique)

        mode = sr.mode()
        mode = mode[0] if not mode.empty else 'None'
        #     mode = mode.strftime('%Y-%m-%d') if (type_ == '<M8[ns]' and mode!='None') else mode

        desc_table = pd.DataFrame([['N', n],
                                   ['N_null', n_null],
                                   ['pct_null', pct_null],
                                   ['N_unique', n_unique],
                                   ['mode', mode]], columns=['Metric', 'Value'])

    source_desc = ColumnDataSource(desc_table)
    columns_desc = [
        TableColumn(field='Metric', title='Metric'),
        TableColumn(field='Value', title='Value')
    ]
    desc_table_ = DataTable(source=source_desc,
                            columns=columns_desc,
                            index_position=None,
                            width=200, height=180)

    table_title = Div(text="""
              <b>Main statistics </b> 
              """,
                      width=150, height=25)

    return column(table_title, desc_table_)