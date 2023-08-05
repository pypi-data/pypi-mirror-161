from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from pandas.core.dtypes.common import is_datetime64_any_dtype


def timeplot(resampled,
              attr,
              date,
              plot_type):

    # add string column of date to resampled df
    # because this will be used for the hovertool
    resampled['date_str'] = resampled.index.strftime('%Y-%m-%d')

    # make datadb
    source = ColumnDataSource(resampled)

    # if the attribute is of type datetime,
    # then the axis should be adjusted
    y_axis_type = 'datetime' if is_datetime64_any_dtype(resampled[attr]) else 'auto'

    # set title and make figuree
    title = f'Quarterly {plot_type} of attribute'
    p = figure(tools="",
               background_fill_color="#efefef",
               x_axis_label=date,
               y_axis_label= plot_type,
               x_axis_type="datetime",
               y_axis_type=y_axis_type,
               toolbar_location=None,
               width=400, height=220,
               title=title)

    # add line
    p.line(date, attr, source=source)

    # Hover tool with vline mode
    hover = HoverTool(tooltips=[(plot_type, attr),
                                ('T', f"@date_str")],
                      mode='vline')
    p.add_tools(hover)

    # further options
    p.title.align = 'center'

    return p