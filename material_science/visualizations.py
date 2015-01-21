"""
Draw a termite plot to visualize topics and words from an LDA.
"""
import blaze as blz
from into import into

import pandas as pd
import bokeh.plotting as plt
import numpy as np

t = blz.Data('material_science/output/simple_termite.csv')
df = pd.read_csv('material_science/output/simple_termite.csv')

# size proportional to result in Karan's example 0-10 range.
MAX =  t.weight.max()
MIN = t.weight.min()

# Create a size variable to define the size of the the circle for the plot.
#t = blz.transform(t, size=np.sqrt((t.weight - MIN)/(MAX - MIN))*50)

data = t

WORDS = data['word'].distinct()
WORDS = into(list, WORDS)

topics = data['topic'].distinct()
topics = into(list, topics)

TOPICS =[]
for topic in topics:
    TOPICS.append(str(topic))

plt.output_file('termite.html')

source = pd.DataFrame(df)

source['weight'] = source['weight'] * 1000
data_source = plt.ColumnDataSource(source)

p = plt.figure(x_range=TOPICS, y_range=WORDS,
       plot_width=1000, plot_height=1700,
       title="Termite Plot", tools='resize, save')

p.circle(x="topic", y="word", size="weight", fill_alpha=0.6, source=data_source)
#p.xaxis().major_label_orientation = np.pi/3
plt.show(p)