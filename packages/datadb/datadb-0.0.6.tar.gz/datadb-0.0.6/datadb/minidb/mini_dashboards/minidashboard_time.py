from bokeh.layouts import column, row
from pandas.core.dtypes.common import is_numeric_dtype, is_string_dtype, is_datetime64_any_dtype

from datadb.minidb.building_blocks.date.timeplot import timeplot
from datadb.minidb.building_blocks.date.timeplot_categorical import timeplot_categorical

from bokeh.models.widgets import Div

def minidashboard_time(df,
                       attr,
                       date):


    df_time = df[[attr, date]].copy(deep=True)

    # resample
    resampled = df_time.set_index(date).resample('q')

    # plot counts
    resampled_count = resampled.count()
    timeplot_counts = timeplot(resampled=resampled_count,
                               attr=attr,
                               date=date,
                               plot_type='count')
    first_column_plots = [timeplot_counts]

    if sum(df[attr].isnull()):
        resampled_notna = df_time.query(f"{attr}.isnull()", engine='python') \
                                 .set_index(date).resample('q').size().to_frame().rename(columns={0:attr})
        timeplot_notna = timeplot(resampled=resampled_notna,
                                    attr=attr,
                                    date=date,
                                    plot_type='count of missing')
        first_column_plots.append(timeplot_notna)

    first_column = column(*first_column_plots)



    if is_numeric_dtype(df[attr]) or is_datetime64_any_dtype(df[attr]):

        # plot sum
        resampled_sum = resampled.sum()
        timeplot_sum = timeplot(resampled = resampled_sum,
                                     attr = attr,
                                     date = date,
                                     plot_type = 'sum')

        # plot mean
        resampled_mean = resampled.mean().query(f"{attr}.notnull()", engine='python')
        timeplot_mean = timeplot(resampled = resampled_mean,
                                     attr = attr,
                                     date = date,
                                     plot_type = 'mean')


        second_column = column(timeplot_sum, timeplot_mean)


    elif is_string_dtype(df[attr]):
        timeplot_categ = timeplot_categorical(df_time, attr, date)
        second_column = column(timeplot_categ)

    db_title = Div(text=""" <b> ============================================  TIME ANALYSIS  ============================================ </b>
                  """,
                   width=800, height=20)
    return column(db_title,
                  row(first_column, second_column))











