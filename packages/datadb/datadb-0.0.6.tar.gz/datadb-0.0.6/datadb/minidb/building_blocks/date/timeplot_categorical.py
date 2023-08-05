import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.plotting import figure
from pandas.core.dtypes.common import is_datetime64_any_dtype


def timeplot_categorical(df_time, attr, date):

    value_counts = (df_time[attr].value_counts(dropna=False)
                      .reset_index()
                      .rename(columns={'index': 'value',
                                       attr: 'counts'})
                    )



    first_6_values = value_counts.query("value.notnull()", engine='python').head(6).value
    n = len(first_6_values)


    df_time_6 = df_time.query(f"{attr} in @first_6_values")

    resampled_df = (df_time_6.set_index(date).groupby([attr, pd.Grouper(freq='q')])
                             .size()
                             .unstack(attr, fill_value=0)
                    )

    resampled_df = resampled_df.sort_index()

    if is_datetime64_any_dtype(df_time[attr]):
        resampled_df.columns = resampled_df.columns.astype(str)

    p = figure(background_fill_color="#efefef",
               y_axis_label=f'Quarterly counts of {attr}',
               x_axis_label=date, x_axis_type="datetime",
               toolbar_location=None,
               width=400, height=300,
               title=f'categorical time plots (for top {n} counts)')

    source = ColumnDataSource(resampled_df)

    colors = Spectral6[0:n]

    for color, col_name in zip(colors, resampled_df.columns):
        p.line(date, col_name, source=source, color=color, legend_label=col_name)

    p.legend.location = "top_left"
    p.xgrid.grid_line_color = "white"
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 1
    p.title.align = 'center'

    p.legend.click_policy = "hide"

    return p