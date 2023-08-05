
from bokeh.models import LinearAxis, Range1d, BasicTickFormatter
from bokeh.plotting import figure


def boxplot(sr):
    sr_notna = sr[sr.notnull()]

    type_ = sr_notna.dtypes

    x = ['normal']
    y_range_name = ['default']

    q1 = sr_notna.quantile(0.25)
    q2 = sr_notna.quantile(0.5)
    q3 = sr_notna.quantile(0.75)

    iqr = q3 - q1
    upper = (q3 + 1.5 * iqr)
    lower = (q1 - 1.5 * iqr)

    outliers = sr_notna[(sr_notna.values > upper) | (sr_notna.values < lower)]

    if not outliers.empty:
        outx = x * len(outliers)
        outy = list(outliers.values)

    # check if makes sense to clip for plot
    big_outliers = ((outliers.values > (upper + iqr)) | (outliers.values < (lower - iqr))).any()

    # # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums

    qmin = min(sr_notna)
    qmax = max(sr_notna)

    upper = min(qmax, upper)
    lower = max(qmin, lower)

    # check if makes sense to clip for plot
    big_outliers = ((outliers.values > (upper + iqr)) | (outliers.values < (lower - iqr))).any()

    if big_outliers:
        # clip outliers to make sure plot axis do not explode
        outliers2 = outliers[(outliers.values <= (upper + iqr)) & (outliers.values >= (lower - iqr))]

        outx2 = ['clipped'] * len(outliers2)
        outy2 = list(outliers2.values)

        x += ['clipped']

    y_axis_type = 'datetime' if type_ == '<M8[ns]' else 'auto'
    p = figure(tools="", background_fill_color="#efefef", toolbar_location=None, width=200, height=300,
               title='Boxplot', x_range=x, y_axis_type=y_axis_type)

    if big_outliers:
        # Setting the second y axis range name and range
        p.extra_y_ranges = {"clipped_y": Range1d(start=lower - iqr,
                                                 end=upper + iqr)}

        # Adding the second axis to the plot.
        p.add_layout(LinearAxis(y_range_name="clipped_y"), 'right')

        y_range_name += ['clipped_y']

    for xi, yi in zip(x, y_range_name):
        p.segment([xi], upper, [xi], q3, line_color='black', y_range_name=yi)
        p.segment([xi], lower, [xi], q1, line_color='black', y_range_name=yi)

        p.vbar([xi], 0.7, q2, q3, fill_color="#E08E79", line_color="black", y_range_name=yi)
        p.vbar([xi], 0.7, q1, q2, fill_color="#3B8686", line_color="black", y_range_name=yi)

        # whiskers (almost-0 height rects simpler than segments)
        p.rect([xi], lower, 0.2, 0.01, line_color="black", y_range_name=yi)
        p.rect([xi], upper, 0.2, 0.01, line_color="black", y_range_name=yi)

    if not outliers.empty:
        p.circle(outx, outy, size=6, color="#F38630", fill_alpha=0.6)

    if big_outliers:
        p.circle(outx2, outy2, size=6, color="#F38630", fill_alpha=0.6, y_range_name=yi)

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size = "10px"
    p.title.align = 'center'

    if not type_ == '<M8[ns]':
        for yax in p.yaxis:
            yax.formatter = BasicTickFormatter(precision=2)

    return p