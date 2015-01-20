from StringIO import StringIO
import os
from itertools import count

from flask import Flask, send_file, request, render_template
from wordcloud import WordCloud
from topic_space.wordcloud_generator import FONT_PATH, get_docs_by_year, get_word_cloud_image


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

TEST_TEXT = """
Butcher stumptown aesthetic, PBR distillery blog normcore 8-bit cronut 3 wolf moon sartorial. Cardigan ethical wolf, paleo leggings fixie Portland pug. Art party authentic Godard, polaroid migas mustache umami messenger bag lo-fi artisan Schlitz literally. Trust fund umami master cleanse sustainable. Pug disrupt hashtag gluten-free flannel. Pug Neutra Brooklyn, vegan 8-bit four dollar toast meditation sustainable pickled Godard Marfa quinoa viral shabby chic. Keytar raw denim locavore, skateboard tousled brunch actually Neutra distillery disrupt roof party McSweeney's scenester.
"""

REQUESTS = {0 : ('1980', '2014', [])} # dictionary of requests id:(year1, year2, words)
REQUEST_COUNTER = count(start=1)
DOCS_DF = get_docs_by_year()

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/wordcloud/', methods=["GET", "POST"])
def wordcloud():
    #import pdb; pdb.set_trace()
    #print("in wordcloud")
    year1 = request.values.get('year1','1980')
    year2 = request.values.get('year2', '2014')
    stop_words = map(lambda x: x.strip(), request.values.get('words','').split('\n'))
    req_id = REQUEST_COUNTER.next()
    REQUESTS[req_id] = (year1, year2, stop_words)
    #print("REQUETS:", REQUESTS)
    #for k, v in request.values.iteritems():
    #    print(k, v)
    return render_template('wordcloud.html', year1=year1, year2=year2, words=stop_words, req_id=req_id)

@app.route('/<req_id>/get_wordcloud.jpg')
def get_wordcloud(req_id):
    year1, year2, stop_words = REQUESTS.get(int(req_id), ("1980", "2014", []))
    year_list = map(str, range(int(year1), int(year2)+1))
    text = DOCS_DF[DOCS_DF['year'].isin(year_list)]['lsa_abs'].sum()
    #print("in get_wordcloud")
    #print("stop_words:", stop_words)
    #print("req_id", req_id)
    #print("REQUESTS:", REQUESTS)
    #    import pdb; pdb.set_trace()
    for word in stop_words:
        text = text.replace(word, '')
    # text = filter(lambda x: x not in stop_words, text.split())
    wordcloud = WordCloud(font_path=FONT_PATH, width=800, height=600).generate(text)
    img_io = StringIO()
    wordcloud.to_image().save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
