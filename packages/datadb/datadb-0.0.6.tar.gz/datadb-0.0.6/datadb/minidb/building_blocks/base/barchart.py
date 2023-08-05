
from bokeh.palettes import Spectral6
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure

def barchart(value_cnts):
    # what we can add:
    # truncate value and add haovertool that shows full name or something
    first_6_counts = value_cnts.query("value.notnull()", engine='python').head(6)
    n = len(first_6_counts)
    first_6_counts['color'] = list(Spectral6)[0:n]

    source = ColumnDataSource(first_6_counts)

    p = figure(x_range=source.data['value'], height=350, title="Top 6 counts",
               toolbar_location=None, tools="", width=550, background_fill_color="#efefef", )

    p.vbar(x='value', top='counts', width=0.9, color='color', source=source)

    labels = LabelSet(x='value', y='counts', text='perc', level='glyph', text_font_size='12px', text_align='center',
                      source=source)
    p.add_layout(labels)

    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.title.align = 'center'

    return p