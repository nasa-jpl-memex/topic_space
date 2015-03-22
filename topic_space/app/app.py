from StringIO import StringIO
import os
from collections import Counter
from uuid import uuid1

from flask import Flask, send_file, request, render_template
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.utils import encode_utf8
from wordcloud import WordCloud

from topic_space.wordcloud_generator import FONT_PATH, get_docs_by_year, read_file, read_sample


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

TEST_TEXT = """
Butcher stumptown aesthetic, PBR distillery blog normcore 8-bit cronut 3 wolf moon sartorial. Cardigan ethical wolf, paleo leggings fixie Portland pug. Art party authentic Godard, polaroid migas mustache umami messenger bag lo-fi artisan Schlitz literally. Trust fund umami master cleanse sustainable. Pug disrupt hashtag gluten-free flannel. Pug Neutra Brooklyn, vegan 8-bit four dollar toast meditation sustainable pickled Godard Marfa quinoa viral shabby chic. Keytar raw denim locavore, skateboard tousled brunch actually Neutra distillery disrupt roof party McSweeney's scenester.
"""

REQUESTS = {0 : ('1980', '2014', [])} # dictionary of requests id:(year1, year2, words)
DOCS_DF = get_docs_by_year()
DF = read_file()
#DF = read_sample(1000)

@app.route('/topic_space/')
def hello_world():
    return 'Hello World!'

@app.route("/topic_space/termite/")
def termite():
    return send_file(os.path.join(tmpl_dir,'termite.html'))

@app.route("/topic_space/diversity/")
def diversity():
    return send_file(os.path.join(tmpl_dir,'diversity.html'))

@app.route("/topic_space/ldavis/")
def ldavis():
    return send_file(os.path.join(tmpl_dir,'ldavis.html'))


@app.route('/topic_space/wordcloud/', methods=["GET", "POST"])
def wordcloud():
    year1 = request.values.get('year1','1980')
    year2 = request.values.get('year2', '2014')
    stop_words = map(lambda x: x.strip(), request.values.get('words','').split('\n'))
    percents = request.values.get("percents", "0% - 100%")
    percent1, percent2 = map(lambda t: int(t.strip()), percents.strip().replace("%", '').split('-'))
    try:
        num_intervals = int(request.values.get('intervals', 1))
    except ValueError:
        num_intervals = 1
    start_years = []
    end_years = []
    year1, year2 = int(year1), int(year2)
    interval_len = (int(year2) - int(year1)) / num_intervals
    for i in range(num_intervals):
        start_years.append(i*interval_len + year1 + i)
        end_years.append(min(year2, start_years[-1] + interval_len))
    req_id = uuid1().get_fields()[0]
    REQUESTS[req_id] = (year1, year2, stop_words, percent1, percent2, num_intervals)
    # Configure resources to include BokehJS inline in the document.
    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#module-bokeh.resources
    plot_resources = RESOURCES.render(
        js_raw=INLINE.js_raw,
        css_raw=INLINE.css_raw,
        js_files=INLINE.js_files,
        css_files=INLINE.css_files,
    )

    plot_scripts, plot_divs = get_bokeh_wordcloud_df(req_id)
    return render_template('wordcloud.html', year1=year1, year2=year2, words=stop_words, req_id=req_id,
                           percent1=percent1, percent2=percent2, num_intervals=num_intervals,
                           start_years=start_years, end_years=end_years,
                           plot_resources=plot_resources, plot_scripts=plot_scripts, plot_divs=plot_divs)


def get_bokeh_wordcloud_df(req_id):
    req = REQUESTS.get(req_id)
    if req:
        num_intervals = req[-1]
    else:
        num_intervals = 1
    plot_scripts = []
    plot_divs = []
    for interval_id in range(num_intervals):
        text_freq = get_word_frequencies(req_id, interval_id)
        fig = figure(title="Word frequency", title_text_font_size="12pt", plot_width=800, plot_height=150, outline_line_color=None, tools="hover")
        source = ColumnDataSource(
            data=dict(
                left=range(len(text_freq)),
                right=[i + 0.7 for i in range(0, len(text_freq))],
                top=map(lambda x: x[1], text_freq),
                word=map(lambda x: x[0], text_freq),
            )
        )
        fig.quad("left", "right", "top", 0, source=source),
        fig.toolbar_location = None
        fig.grid.grid_line_color = None
        fig.xaxis.axis_line_color = None
        fig.xaxis.major_tick_line_color = None
        fig.xaxis.minor_tick_line_color = None
        fig.xaxis.major_label_text_color = None
        fig.yaxis.minor_tick_line_color = None
        hover = fig.select(dict(type=HoverTool))
        hover.tooltips = [
        ("word", "@word"),
        ("frequency", "@top"),
        ("fill color", "$color[hex, swatch]:fill_color"),
        ]
        script, div = components(fig, INLINE)
        plot_scripts.append(script)
        plot_divs.append(div)
    return plot_scripts, plot_divs


def get_word_frequencies(req_id, interval_id):
    year1, year2, stop_words, percent1, percent2, num_intervals = REQUESTS.get(int(req_id), ("1980", "2014", [], 0, 100, 1))
    year1, year2, interval_id = map(int, [year1, year2, interval_id])
    interval_len = (int(year2) - int(year1)) / num_intervals
    year1 = interval_len * interval_id + year1 + interval_id
    year2 = min(year2, year1+interval_len)
    year_list = map(str, range(year1, year2+1))
    print("year1:", year1, "year2:", year2, "num_intervals", num_intervals, "interval_len", interval_len)
    text = DOCS_DF[DOCS_DF['year'].isin(year_list)]['lsa_abs'].sum()
    stop_words = set(map(lambda t: t.strip().lower(), stop_words))
    text_list = map(lambda t: t.strip().lower(), text.split())
    text_counter = Counter(text_list)
    text_freq = list(text_counter.iteritems())
    text_freq = filter(lambda x: x[0] not in stop_words, text_freq)
    text_freq.sort(key=lambda x: x[1])
    low_count = int(len(text_freq) * (percent1 * .01))
    high_count = int(len(text_freq) * (percent2 * .01))
    print("precents", percent1, percent2)
    print("len(text_freq)", len(text_list), "low_count", low_count, "high_count", high_count)
    text_freq = text_freq[low_count:high_count]
    return text_freq[-100:]


@app.route('/topic_space/<req_id>/<interval_id>/get_wordcloud.jpg')
def get_wordcloud(req_id, interval_id):
    text_freq = get_word_frequencies(req_id, interval_id)
    wordcloud = WordCloud(font_path=FONT_PATH, width=800, height=600)
    wordcloud.fit_words(list(reversed(text_freq[-100:])))
    img_io = StringIO()
    wordcloud.to_image().save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


colors = {
    'Black': '#000000',
    'Red':   '#FF0000',
    'Green': '#00FF00',
    'Blue':  '#0000FF',
}


def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]



@app.route('/topic_space/histogram/', methods=["GET", "POST"])
def histogram():
    # Grab the inputs arguments from the URL
    # This is automated by the button
    args = request.args

    # Get all the form arguments in the url with defaults
    color = colors[getitem(args, 'color', 'Black')]
    _from = int(getitem(args, '_from', 0))
    to = int(getitem(args, 'to', 10))

    count_df = DF[['year', 'abstract']].groupby('year').count()
    count_df = count_df.drop("January 2000")
    fig = figure(title="Histogram of Docs Per Year")
    fig.line(map(int, count_df.index), list(count_df['abstract']), color=color, line_width=2)

    # Configure resources to include BokehJS inline in the document.
    # For more details see:
    #   http://bokeh.pydata.org/en/latest/docs/reference/resources_embedding.html#module-bokeh.resources
    plot_resources = RESOURCES.render(
        js_raw=INLINE.js_raw,
        css_raw=INLINE.css_raw,
        js_files=INLINE.js_files,
        css_files=INLINE.css_files,
    )

# For more details see:
#   http://bokeh.pydata.org/en/latest/docs/user_guide/embedding.html#components
    script, div = components(fig, INLINE)
    html = render_template(
        'histogram.html',
        plot_script=script, plot_div=div, plot_resources=plot_resources,
        color=color, _from=_from, to=to
    )
    return encode_utf8(html)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8017)
