from StringIO import StringIO
import os

from flask import Flask, send_file, request, render_template
from wordcloud import WordCloud
from topic_space.wordcloud_generator import FONT_PATH

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

TEST_TEXT = """
Butcher stumptown aesthetic, PBR distillery blog normcore 8-bit cronut 3 wolf moon sartorial. Cardigan ethical wolf, paleo leggings fixie Portland pug. Art party authentic Godard, polaroid migas mustache umami messenger bag lo-fi artisan Schlitz literally. Trust fund umami master cleanse sustainable. Pug disrupt hashtag gluten-free flannel. Pug Neutra Brooklyn, vegan 8-bit four dollar toast meditation sustainable pickled Godard Marfa quinoa viral shabby chic. Keytar raw denim locavore, skateboard tousled brunch actually Neutra distillery disrupt roof party McSweeney's scenester.
"""

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/wordcloud/', methods=["GET", "POST"])
def wordcloud():
    #    import pdb; pdb.set_trace()
    year1 = request.values['year1']
    year2 = request.values['year2']
    stop_words = request.values['words'].split(',')
    for k, v in request.values.iteritems():
        print(k, v)
    return render_template('wordcloud.html', year1=year1, year2=year2, words=stop_words)

@app.route('/get_wordcloud.jpg')
def get_wordcloud():
    wordcloud = WordCloud(font_path=FONT_PATH, width=800, height=600).generate(TEST_TEXT)
    img_io = StringIO()
    wordcloud.to_image().save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
