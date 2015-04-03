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
from wordcloud import WordCloud

from topic_space.wordcloud_generator import FONT_PATH, load_docs


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

TEST_TEXT = """
Butcher stumptown aesthetic, PBR distillery blog normcore 8-bit cronut 3 wolf moon sartorial. Cardigan ethical wolf, paleo leggings fixie Portland pug. Art party authentic Godard, polaroid migas mustache umami messenger bag lo-fi artisan Schlitz literally. Trust fund umami master cleanse sustainable. Pug disrupt hashtag gluten-free flannel. Pug Neutra Brooklyn, vegan 8-bit four dollar toast meditation sustainable pickled Godard Marfa quinoa viral shabby chic. Keytar raw denim locavore, skateboard tousled brunch actually Neutra distillery disrupt roof party McSweeney's scenester.
"""

DOCS_DF = load_docs()
print("Loaded documents")
#DF = read_file()
#DF = read_sample(1000)


class RequestData:

    def __init__(self, year1, year2, stop_words=None, percent1=0, percent2=100, num_intervals=1):
        self.year1 = int(year1)
        self.year2 = int(year2)
        self.stop_words = stop_words if stop_words is not None else []
        self.percent1 = percent1
        self.percent2 = percent2
        self.num_intervals = min(int(num_intervals), self.year2 - self.year1)
        self.interval_len = (self.year2 - self.year1) / self.num_intervals

    def get_interval_data(self, interval_id):
        interval_id = int(interval_id)
        interval_begin = self.interval_len * interval_id + self.year1
        interval_end = min(self.year2, interval_begin + self.interval_len)
        year_list = map(str, range(interval_begin, interval_end+1))
        return interval_begin, interval_end, year_list

    def get_interval_num_docs(self, interval_id):
        _, _, year_list = self.get_interval_data(interval_id)
        return DOCS_DF[DOCS_DF['year'].isin(year_list)]['num_docs'].sum()

    def get_num_docs(self):
        return map(lambda interval_id: self.get_interval_num_docs(interval_id),
                   range(self.num_intervals))

    def get_word_frequencies(self, interval_id):
        interval_begin, interval_end, year_list = self.get_interval_data(interval_id)
        text = DOCS_DF[DOCS_DF['year'].isin(year_list)]['lsa_abs'].sum()
        stop_words = set(map(lambda t: t.strip().lower(), self.stop_words))
        text_list = map(lambda t: t.strip().lower(), text.split())
        text_counter = Counter(text_list)
        text_freq = list(text_counter.iteritems())
        text_freq = filter(lambda x: x[0] not in stop_words, text_freq)
        text_freq.sort(key=lambda x: x[1])
        low_count = int(len(text_freq) * (self.percent1 * .01))
        high_count = int(len(text_freq) * (self.percent2 * .01))
        text_freq = text_freq[low_count:high_count]
        return text_freq[-100:]

    def get_wordcloud_img(self, interval_id):
        text_freq = self.get_word_frequencies(interval_id)
        wordcloud = WordCloud(font_path=FONT_PATH, width=800, height=600)
        wordcloud.fit_words(list(reversed(text_freq[-100:])))
        img_io = StringIO()
        wordcloud.to_image().save(img_io, 'JPEG', quality=70)
        img_io.seek(0)
        return img_io

    def get_bokeh_word_frequencies(self):
        plot_scripts = []
        plot_divs = []
        for interval_id in range(self.num_intervals):
            text_freq = self.get_word_frequencies(interval_id)
            fig = figure(title="Word frequency", title_text_font_size="12pt", plot_width=800, plot_height=150,
                         outline_line_color=None, tools="hover")
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



REQUESTS = {0: RequestData('1980', '2014', [])}


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


def cache_request():
    year1 = request.values.get('year1', '1980')
    year2 = request.values.get('year2', '2014')
    stop_words = map(lambda x: x.strip(), request.values.get('words','').split('\n'))
    percents = request.values.get("percents", "0% - 100%")
    percent1, percent2 = map(lambda t: int(t.strip()), percents.strip().replace("%", '').split('-'))
    try:
        num_intervals = int(request.values.get('intervals', 1))
    except ValueError:
        num_intervals = 1
    year1, year2 = int(year1), int(year2)
    req_id = uuid1().get_fields()[0]
    REQUESTS[req_id] = RequestData(year1, year2, stop_words, percent1, percent2, num_intervals)
    return req_id


@app.route('/topic_space/wordcloud/', methods=["GET", "POST"])
def wordcloud():
    req_id = cache_request()
    req = REQUESTS[req_id]

    start_years = []
    end_years = []
    for i in range(req.num_intervals):
        start_years.append(i*req.interval_len + req.year1)
        end_years.append(min(req.year2, start_years[-1] + req.interval_len))
    plot_resources = RESOURCES.render(
        js_raw=INLINE.js_raw,
        css_raw=INLINE.css_raw,
        js_files=INLINE.js_files,
        css_files=INLINE.css_files,
    )

    plot_scripts, plot_divs = req.get_bokeh_word_frequencies()
    num_docs = req.get_num_docs()
    return render_template('wordcloud.html', year1=req.year1, year2=req.year2, words=req.stop_words, req_id=req_id,
                           percent1=req.percent1, percent2=req.percent2, num_intervals=req.num_intervals,
                           start_years=start_years, end_years=end_years,
                           plot_resources=plot_resources, plot_scripts=plot_scripts, plot_divs=plot_divs,
                           num_docs=num_docs)


@app.route('/topic_space/<req_id>/<interval_id>/get_wordcloud.jpg')
def wordcloud_img(req_id, interval_id):
    req = REQUESTS.get(int(req_id), REQUESTS[0])
    return send_file(req.get_wordcloud_img(interval_id), mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8017)
