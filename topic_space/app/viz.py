from __future__ import absolute_import
"""
Draw a termite plot to visualize topics and words from an LDA.
"""

import logging

import blaze as blz
from odo import into
import pandas as pd
import bokeh.plotting as plt
from bokeh.models.sources import ColumnDataSource
from bokeh.embed import components
from bokeh.resources import CDN

class Termite(object):

    def __init__(self, input_file):
        self.input_file = input_file

    def plot(self):
        t = blz.Data(self.input_file)
        df = pd.read_csv(self.input_file)

        MAX =  blz.compute(t.weight.max())
        MIN = blz.compute(t.weight.min())

        # Create a size variable to define the size of the the circle for the plot.
        t = blz.transform(t, size=blz.sqrt((t.weight - MIN)/(MAX - MIN))*50)

        WORDS = t['word'].distinct()
        WORDS = into(list, WORDS)
        topics = t['topic'].distinct()
        topics = into(list, topics)
        # Convert topics to strings
        TOPICS = [str(i) for i in topics]

        source = into(pd.DataFrame, t)

        data_source = ColumnDataSource(source)

        p = plt.figure(x_range=TOPICS, y_range=WORDS,
               plot_width=1000, plot_height=1700, title=None)

        p.circle(x="topic", y="word", size="size", fill_alpha=0.6, source=data_source)
        #p.xaxis().major_label_orientation = np.pi/3
        logging.info("generating termite plot for file %s" % self.input_file)

        script, div = components(p, CDN)

        return script, div
