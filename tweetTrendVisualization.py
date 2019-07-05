import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
import pandas as pd

#popular topics: google, olympics, trump, gun, usa

# it's ok to use one shared sqlite connection
# as we are making selects only, no need for any kind of serialization as well
conn = sqlite3.connect('twitter.db', check_same_thread=False)

MAX_DF_LENGTH = 100

app = dash.Dash(__name__)
app.layout = html.Div(
    [   html.H2('Live Twitter Sentiment'),
        html.H5('Search:'),
        dcc.Input(id='sentiment_term', value='twitter', type='text'),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ]
)

def df_resample_sizes(df, maxlen=MAX_DF_LENGTH):
    df_len = len(df)
    resample_amt = 100
    vol_df = df.copy()
    vol_df['volume'] = 1

    ms_span = (df.index[-1] - df.index[0]).seconds * 1000
    rs = int(ms_span / maxlen)

    df = df.resample('{}ms'.format(int(rs))).mean()
    df.dropna(inplace=True)

    vol_df = vol_df.resample('{}ms'.format(int(rs))).sum()
    vol_df.dropna(inplace=True)

    df = df.join(vol_df['volume'])

    return df

@app.callback(Output('live-graph', 'figure'),
            [Input(component_id='sentiment_term', component_property='value'),
            Input('graph-update', 'n_intervals')])
              # events=[Event('graph-update', 'interval')])

def update_graph_scatter(sentiment_term, n):
    try:
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn ,params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df.dropna(inplace=True)
        df['date'] = pd.to_datetime(df['unix'], unit='ms')
        df.set_index('date', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df = df_resample_sizes(df)
        X = df.index[-100:]
        Y = df.sentiment_smoothed.values[-100:]

        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Sentiment',
                mode= 'lines',
                )

        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),max(Y)]),
                                                    title='Live sentiment for: {}'.format(sentiment_term))}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')

server = app.server
dev_server = app.run_server