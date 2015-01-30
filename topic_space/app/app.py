from StringIO import StringIO
import os
from itertools import count
from collections import Counter

from flask import Flask, send_file, request, render_template
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.utils import encode_utf8
from wordcloud import WordCloud

from topic_space.wordcloud_generator import FONT_PATH, get_docs_by_year, read_file


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

TEST_TEXT = """
Butcher stumptown aesthetic, PBR distillery blog normcore 8-bit cronut 3 wolf moon sartorial. Cardigan ethical wolf, paleo leggings fixie Portland pug. Art party authentic Godard, polaroid migas mustache umami messenger bag lo-fi artisan Schlitz literally. Trust fund umami master cleanse sustainable. Pug disrupt hashtag gluten-free flannel. Pug Neutra Brooklyn, vegan 8-bit four dollar toast meditation sustainable pickled Godard Marfa quinoa viral shabby chic. Keytar raw denim locavore, skateboard tousled brunch actually Neutra distillery disrupt roof party McSweeney's scenester.
"""

REQUESTS = {0 : ('1980', '2014', [])} # dictionary of requests id:(year1, year2, words)
REQUEST_COUNTER = count(start=1)
DOCS_DF = get_docs_by_year()
DF = read_file()

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
    req_id = REQUEST_COUNTER.next()
    REQUESTS[req_id] = (year1, year2, stop_words, percent1, percent2, num_intervals)
    return render_template('wordcloud.html', year1=year1, year2=year2, words=stop_words, req_id=req_id,
                           percent1=percent1, percent2=percent2, num_intervals=num_intervals,
                           start_years=start_years, end_years=end_years)


@app.route('/topic_space/<req_id>/<interval_id>/get_wordcloud.jpg')
def get_wordcloud(req_id, interval_id):
    year1, year2, stop_words, percent1, percent2, num_intervals = REQUESTS.get(int(req_id), ("1980", "2014", [], 0, 100, 1))
    year1, year2, interval_id = map(int, [year1, year2, interval_id])
    interval_len = (int(year2) - int(year1)) / num_intervals
    year1 = interval_len * interval_id + year1 + interval_id
    year2 = min(year2, year1+interval_len)
    year_list = map(str, range(year1, year2+1))
    print( "year1:", year1, "year2:", year2, "num_intervals", num_intervals, "interval_len", interval_len)
    text = DOCS_DF[DOCS_DF['year'].isin(year_list)]['lsa_abs'].sum()
    stop_words = set(map(lambda t: t.strip().lower(), stop_words))
    text_list = map(lambda t: t.strip().lower(), text.split())
    text_counter = Counter(text_list)
    text_cw = list(text_counter.iteritems())
    text_cw.sort(key=lambda x: x[1])
    low_count = int(len(text_cw) * (percent1 * .01))
    high_count = int(len(text_cw) * (percent2 * .01))
    print("precents", percent1, percent2)
    print("len(text_list)", len(text_list), "low_counnt", low_count, "high_count", high_count)
    filter_words = map(lambda x: x[0], text_cw[low_count:high_count])
#    import pdb; pdb.set_trace()
    print("len(filter_words)", len(filter_words), "filter_words[:10]", filter_words[:10])
    filter_words = set(filter_words)
    text_list = filter(lambda t: t in filter_words, text_list)
    print("len(text_list)", len(text_list))
    text_list = filter(lambda t: t not in stop_words, text_list)
    print("len(text_list)", len(text_list))
    text = " ".join(text_list)
    wordcloud = WordCloud(font_path=FONT_PATH, width=800, height=600).generate(text)
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
