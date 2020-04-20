import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import pandas as pd


VERSION = 2020.0
data_dir = 'https://raw.githubusercontent.com/AnttiHaerkoenen/grand_duchy/master/data/processed/'

languages = {
    'Finnish': 'fi',
    'Swedish': 'sv',
    # 'English': 'en',
}


def get_distances(
        language,
        kw1,
        kw2,
        data,
):
    if not kw1 or not kw2:
        return None, None

    lang_data = data.get(language)

    x = []
    y = []

    for year, m in lang_data.items():
        if kw1 in m.index and kw2 in m.index:
            y.append(m.loc[kw1, kw2])
            x.append(year)

    return x, y


distance_data = {
    'fi': {
        year: pd.read_csv(data_dir + f'distance_matrix_fi_{year}.csv', index_col=0)
        for year
        in range(1820, 1881, 20)
    },
    'sv': {
        year: pd.read_csv(data_dir + f'distance_matrix_sv_{year}.csv', index_col=0)
        for year
        in range(1740, 1901, 20)
    },
    # 'en': {
    #     year: pd.read_csv(data_dir + f'distance_matrix_en_{year}.csv', index_col=0)
    #     for year
    #     in range(1820, 1881, 20)
    # }
}

keyword_options = {
    lang: [''] + sorted({
        kw
        for year_data in lang_data.values()
        for kw in year_data.index
    })
    for (lang, lang_data)
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
        ),
    ]),

    html.Div([
        html.H2(children='Select comparison keywords'),

        html.H4(children='Keyword 1'),

        dcc.Dropdown(
            id='keyword-picker-1',
        ),

        html.H4(children='Keyword 2'),

        dcc.Dropdown(
            id='keyword-picker-2',
        ),

        html.H4(children='Keyword 3'),

        dcc.Dropdown(
            id='keyword-picker-3',
        ),
    ]),

    html.Div([
        html.H2(id='graph-title'),

        dcc.Graph(id='line-plot'),
    ]),


    html.P(
        children=f"Version {VERSION}",
        style={
            'font-style': 'italic'
        },
    ),
])


@app.callback(
    Output('keyword-picker', 'options'),
    [
        Input('language-picker', 'value'),
    ]
)
def set_keyword_options(
        language,
):
    kw_options = [
        {'label': kw, 'value': kw}
        for kw
        in keyword_options.get(language, ())
    ]
    return kw_options


@app.callback(
    [
        Output('keyword-picker-1', 'options'),
        Output('keyword-picker-2', 'options'),
        Output('keyword-picker-3', 'options'),
    ],
    [
        Input('language-picker', 'value'),
        Input('keyword-picker', 'value'),
    ]
)
def set_other_keyword_options(
        language,
        first_keyword,
):
    updated_kws = keyword_options.get(language, ())

    if first_keyword in updated_kws:
        updated_kws.remove(first_keyword)

    updated_kw_options = [
        {'label': kw, 'value': kw}
        for kw
        in updated_kws
    ]

    return updated_kw_options, updated_kw_options, updated_kw_options


@app.callback(
    Output('graph-title', 'children'),
    [
        Input('keyword-picker', 'value'),
    ]
)
def update_graph_title(
        keyword,
):
    return f"Cosine similarity to '{keyword}'"



@app.callback(
    Output('line-plot', 'figure'),
    [
        Input('language-picker', 'value'),
        Input('keyword-picker', 'value'),
        Input('keyword-picker-1', 'value'),
        Input('keyword-picker-2', 'value'),
        Input('keyword-picker-3', 'value'),
    ]
)
def update_graph(
        language,
        keyword,
        *other_keywords,
):
    if not keyword:
        raise PreventUpdate

    data = []

    for kw in other_keywords:
        x, y = get_distances(
            language,
            keyword,
            kw,
            distance_data,
        )

        data.append(
            {
                'x': x,
                'y': y,
                'name': kw,
            }
        )

    return {
        'data': data,
    }


if __name__ == '__main__':
    app.run_server(
        port=8080,
        host='0.0.0.0',
        debug=True,
    )
