from bokeh.layouts import column

from datadb.minidb.building_blocks.target.target_info import target_info
from bokeh.models.widgets import Div

def minidashboard_target(df, attr, target):
    db_title = Div(text=""" <b> ===============================================  TARGET  =============================================== </b>
                  """,
                   width=800, height=20)
    return column(db_title,
        target_info(df, attr, target))