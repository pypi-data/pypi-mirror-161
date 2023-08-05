import pandas as pd
import inspect

from bokeh.layouts import column

from datadb.minidb.mini_dashboards.minidashboard_base import minidashboard_base
from datadb.minidb.mini_dashboards.minidashboard_time import minidashboard_time
from datadb.minidb.mini_dashboards.minidashboard_target import minidashboard_target

from bokeh.plotting.figure import Figure

from bokeh.io import output_notebook, show
from bokeh.resources import INLINE

output_notebook(resources=INLINE)

def find_table(attr: str,
               date: str = None,
               target: str = None):



    dfs = [df for k, df in inspect.currentframe().f_back.f_back.f_locals.items()
           if isinstance(df, pd.core.frame.DataFrame) and not k.startswith('_')]



    cols = [attr]
    cols = cols + [date] if date else cols
    cols = cols + [target] if target else cols

    dfs_possible = [df for df in dfs if all([c in df.columns for c in cols])]

    if len(dfs_possible) > 1:


        print(dfs_possible[0] is dfs_possible[1])
        # print('are same?' , dfs_possible[0] == dfs_possible[1])
        # for dd in dfs_possible:
        #
        #     print(dd.columns)
        # print('error')
    else:
        df = dfs_possible[0]

    return df


def mdb(attr: str,
        date: str = None,
        target: str = None,
        df: pd.DataFrame = None):

    df = df if df is not None else find_table(attr, date, target)


    mdb_base = minidashboard_base(df, attr)
    mdbs = [mdb_base]

    if date:
        mdb_time = minidashboard_time(df, attr, date)
        mdbs.append(mdb_time)
    if target:

        mdb_target = minidashboard_target(df, attr, target)
        mdbs.append(mdb_target)

    layout = column(*mdbs, background ='beige')

    def all_figures(start_element):
        if isinstance(start_element, Figure):
            yield start_element
        elif 'children' in dir(start_element):
            for c in start_element.children:
                yield from all_figures(c)

    for c in all_figures(layout):
        c.border_fill_color = "beige"

    show(layout)








