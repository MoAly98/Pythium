import pandas as pd
import numpy as np

event1 = {'njets': ['jet1', 'jet2', 'jet3'],
          'colour': ['colour1', 'colour2', 'colour3']}
event2 = {'njets': ['jet1', 'jet2', 'jet3', 'jet4'],
          'colour': ['colour1', 'colour2', 'colour3', 'colour4']}

df1 = pd.DataFrame(event1)
# df1.columns = ['njets', 'colour']
# df1['event'] = "event1"

df2 = pd.DataFrame(event2)
# df2.columns = ['njets', 'colour']
# df2['event'] = "event2"



print(df1)
print('---')
print(df2)
print('---')

total = pd.concat([df1, df2], keys=['event1', 'event2'])
print(total)
print('---')

# total.set_index(['event', 'njets'   ], inplace=True)
# print(total)
# print('---')


events = ['event1', 'event2', 'event3']

jets1 = ['j1', 'j2']
jets2 = ['j1', 'j2', 'j3']
jets3 = ['j1']

df1 = pd.DataFrame(jets1)
df1.columns = events[0]

print(df1)

data = {'jet':[jets1, jets2, jets3]}
df = pd.DataFrame(data, index=events)

print(df)
print(df.index)
