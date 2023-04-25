from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
from worldcloud_component_dash_component import WorldcloudComponentDashComponent
import pandas as pd
import plotly.express as px
import numpy as np

df = pd.read_csv("data_keywords_covid_19.csv", sep="\t",index_col=0)
start_date= "2020-01-01"
end_date = "2021-12-31"
available_dates = df.date.unique().tolist()
unavailable_days = [day.to_pydatetime().strftime("%Y-%m-%d") for day in pd.date_range(start_date, end_date, freq="D") ]
unavailable_days = [day for day in unavailable_days if not day in available_dates]
keywords_available = df.term.unique()


def generate_bar_plot(dataframe, keywords, bar=False):
    df_viz = dataframe[dataframe.term.isin(keywords)].copy()

    if not bar:
        fig = px.line(df_viz, x="date", y="freq", color="term", hover_name="term",
                      color_discrete_sequence=px.colors.qualitative.Dark24, line_shape="spline", render_mode="svg")
    else:
        fig = px.bar(df_viz, x="date", y="freq", color="term", hover_name="term",
                     color_discrete_sequence=px.colors.qualitative.Dark24)

    fig.update_layout(yaxis_title="# keywords ")
    fig.update_xaxes(rangeslider_visible=True)
    return fig


app = Dash(__name__,
           external_stylesheets=[
               dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Open+Sans&display=swap"],
           title="Keywords Explorer")

app.css.config.serve_locally = True


app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Ngram-Viewer : Assemblée Nationale durant la pandémie Covid-19 (Janvier 2020 et Décembre 2021)",
                    className="text-center")
        ]),
        html.Div(id="search-bar", children=[
            dcc.Dropdown(df.term.unique(), value=[
                         "covid-19"], multi=True, id="search-bar-form", persistence=True, persistence_type="session"),
            html.Div([
                html.H4("Paramètres"),
                dbc.Switch(label="Diagramme à barre ?",
                           value=False, id="bar-plot-switch")
            ], id="parameters")

        ]),
        html.Div([
            dbc.Spinner(
                [dcc.Graph(figure={}, id="plot-keywords-bar")], color="danger", type="grow"
            ),
            html.Div([
                html.Div(id="parameters_wordcloud", children=[
                    html.H4("Paramètres"),
                    html.Label("Jour: ", htmlFor="date_picker_wordcloud"),
                    dcc.DatePickerSingle(id="date_picker_wordcloud",
                                         min_date_allowed="2020-01-01",
                                         max_date_allowed="2021-12-31",
                                         date="2020-01-15", first_day_of_week=1,
                                         display_format="YYYY-M-D",disabled_days=unavailable_days)
                ]),

                dbc.Spinner(color="primary", children=[
                    html.Div([

                        ], id="wordcloudDiv")
                ]),



            ])

        ], id="plot")
    ])
], className="container", style={"font-family": "'Open Sans', sans-serif"})


@app.callback(inputs=[Input(component_id="search-bar-form", component_property="value"),
                      Input(component_id="bar-plot-switch", component_property="value")],
              output=Output(component_id="plot-keywords-bar", component_property="figure"))
def update_bar_plot(values, is_bar_plot):
    return generate_bar_plot(df, values, is_bar_plot)


@app.callback(output=Output(component_id="wordcloudDiv", component_property="children"),
              inputs=[Input('date_picker_wordcloud', 'date')])
def update_word_cloud(date):
    df_on_date = df[(df.date == date)].sort_values(
        "freq", ascending=False).head(50)
    df_on_date["freq"] /= df_on_date.freq.max()
    df_on_date = df_on_date["term freq".split()].rename(columns={"freq":"#","term":"Mot-clé"})
    return html.Div([
            html.Div(
                WorldcloudComponentDashComponent(shape="diamond",
                                width=1200, height=400,
                                list=df_on_date.values.tolist(), weightFactor=100,
                                fontFamily="'Open Sans', sans-serif")
                ,className="col-lg-7 col-sm-12 d-flex flex-column min-vh-0 justify-content-center align-items-center"),
            html.Div(
                dash_table.DataTable(
                    df_on_date.to_dict('records'), [{"name": i, "id": i} for i in df_on_date.columns],
                    style_as_list_view=True,
                    page_size=15,
                    style_cell={'padding': '5px'},
                    style_header={
                        'backgroundColor': '#efefef',
                        'fontWeight': 'bold',
                        "font-family":"'Open Sans', sans-serif"
                    },
                    style_data={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                         "font-family":"'Open Sans', sans-serif"
                    })
            ,className="col-lg-4 col-sm-12 p-1")
        ],className="row mt-3",style={"height":"500px"})


if __name__ == '__main__':
    app.run_server(debug=True)
