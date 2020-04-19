import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import pandas as pd

VERSION = 2020.0
data_dir = 'https://raw.githubusercontent.com/AnttiHaerkoenen/grand_duchy/master/data/processed/'

languages = {
    'Finnish': 'fi',
    'Swedish': 'sv',
    # 'English': 'en',
}

distance_data = {
    'fi': {
        year: pd.read_csv(data_dir + f'distance_matrix_fi_{year}.csv')
        for year
        in range(1820, 1881, 20)
    },
    'sv': {
        year: pd.read_csv(data_dir + f'distance_matrix_sv_{year}.csv')
        for year
        in range(1740, 1901, 20)
    },
    # 'en': {
    #     year: pd.read_csv(data_dir + f'distance_matrix_en_{year}.csv')
    #     for year
    #     in range(1820, 1881, 20)
    # }
}

keywords = {
    l: {
        kw
        for year_data in lang_data.values()
        for kw in year_data.index
    }
    for (l, lang_data)
    in distance_data.items()
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)
app.title = "Word distances"

application = app.server

language_options = [
    {'label': k, 'value': v}
    for (k, v)
    in languages.items()
]

app.layout = html.Div(children=[
    html.H1(children=f'{app.title}'),

    html.Div([
        html.H2(children='Select Language'),

        dcc.Dropdown(
            id='language-picker',
            options=language_options,
            value=language_options[0]['value'],
        ),
    ]),

    html.Div([
        html.H2(children='Select Keyword'),

        dcc.Dropdown(
            id='keyword-picker',
            options=keywords,
            value=keywords[0]['value'],
        ),
    ]),

    dcc.Graph(id='line-plot'),

    html.P(
        children=f"Version {VERSION}",
        style={
            'font-style': 'italic'
        },
    ),
])


@app.callback(
    Output('line-plot', 'figure'),
    [Input('keyword-picker', 'value'),
     Input('abs-picker', 'value'),]
)
def update_graph(
        keyword,
        abs_or_rel,
):
    x = data['year']
    y = data[keyword]

    return {
        'data': [{
            'x': x,
            'y': y,
            'type': 'line',
            'name': keyword,
        }]
    }


if __name__ == '__main__':
    app.run_server(
        port=8080,
        # host='0.0.0.0',
        debug=True,
    )
