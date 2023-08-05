import numpy as np
import pandas as pd

import math

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure


def histogram(sr):
    def make(p_low: float = 1.25,
             p_high: float = 98.75,
             density: bool = False,
             bins: int = 30):

        n_digits = 3

        def round_to_n_digits(x):
            return round(x, n_digits - int(math.floor(math.log10(abs(x)))) - 1) if x else x

        def my_round(x):
            return round(x) if abs(x) > (10 ** (n_digits - 1)) else round_to_n_digits(x)

        def my_format(x):
            return f"{my_round(x):,}"


        sr_notna = sr[sr.notnull()]

        type_ = sr.dtypes

        q_low = sr_notna.quantile(p_low / 100)
        q_high = sr_notna.quantile(p_high / 100)

        wo_outliers = sr_notna[(sr_notna.values > q_low) & (sr_notna.values < q_high)]

        if type_ == '<M8[ns]':
            wo_outliers = wo_outliers.values.astype(np.int64) // 10 ** 9
            hist, edges = np.histogram(wo_outliers, density=density, bins=bins)

            df_hist = pd.DataFrame({'values': hist,
                                    'left': pd.to_datetime(edges[:-1], unit='s'),
                                    'right': pd.to_datetime(edges[1:], unit='s')})

            df_hist['values_show'] = [f'{x:.2%}' if density else my_format(x) for x in df_hist['values']]

            df_hist['interval_str'] = [f"{left.strftime('%Y-%m-%d')} to {right.strftime('%Y-%m-%d')}"
                                       for left, right in zip(df_hist['left'], df_hist['right'])]
        else:

            hist, edges = np.histogram(wo_outliers, density=density, bins=bins)

            df_hist = pd.DataFrame({'values': hist,
                                    'left': edges[:-1],
                                    'right': edges[1:]})

            df_hist['values_show'] = [f'{x:.2%}' if density else my_format(x) for x in df_hist['values']]
            df_hist['interval_str'] = [f'{my_format(left)} to {my_format(right)}'
                                       for left, right in zip(df_hist['left'], df_hist['right'])]

        src = ColumnDataSource(df_hist)

        # make plot
        x_axis_type = 'datetime' if type_ == '<M8[ns]' else 'auto'
        y_axis_label = 'percentage' if density else 'counts'
        p = figure(title=f'Histogram between Perc {p_low} and Perc {p_high} ',
                   background_fill_color="#fafafa",
                   width=400, height=250,
                   x_axis_type=x_axis_type,
                   y_axis_label=y_axis_label)

        p.quad(source=src, bottom=0, top='values', left='left', right='right',
               fill_alpha=0.7,
               hover_fill_alpha=1.0, line_color='black')

        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('Bin edges', '@interval_str'),
                                    ('Value', '@values_show')],
                          mode='vline')

        p.add_tools(hover)
        p.title.align = 'center'
        return p

    p = make()
    p.toolbar_location = None

    return p