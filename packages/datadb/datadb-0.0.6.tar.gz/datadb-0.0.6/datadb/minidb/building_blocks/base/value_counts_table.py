from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn


def valuecountstable(value_cnts):
    type_ = value_cnts.dtypes.value
    value_cnts_ = value_cnts.copy(deep=True)
    if type_ == '<M8[ns]':
        value_cnts_['value'] = value_cnts_['value'].dt.strftime('%Y-%m-%d')
    source_value_cnts = ColumnDataSource(value_cnts_)
    columns_value_cnts = [TableColumn(field='value', title='value'),
                          TableColumn(field='counts', title='counts'),
                          TableColumn(field='perc', title='perc')]
    value_cnts_table = DataTable(source=source_value_cnts, columns=columns_value_cnts, autosize_mode='fit_columns',
                                 width=300, height=200, index_position=None)
    return value_cnts_table
