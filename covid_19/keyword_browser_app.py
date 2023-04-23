from dash import Dash, html, dcc, Input,Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

df = pd.read_csv("data_keywords_covid_19.csv",sep="\t")
keywords_available = df.term.unique()

def generate_bar_plot(dataframe,keywords,bar=False):
    df_viz = dataframe[dataframe.term.isin(keywords)].copy()
    if not bar:
        fig = px.line(df_viz, x="date", y="freq", color="term", hover_name="term",color_discrete_sequence=px.colors.qualitative.Dark24
                ,line_shape="spline", render_mode="svg")
    else:
        fig = px.bar(df_viz, x="date", y="freq", color="term", hover_name="term",color_discrete_sequence=px.colors.qualitative.Dark24)
    
    fig.update_layout( yaxis_title="# keywords ")
    fig.update_xaxes(rangeslider_visible=True)
    return fig

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP,"https://fonts.googleapis.com/css2?family=Open+Sans&display=swap"])
app.css.config.serve_locally = True

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Ngram-Viewer : Assemblée Nationale durant la pandémie Covid-19 (Janvier 2020 et Décembre 2021)"
                    ,className="text-center")
        ]),
        html.Div(id="search-bar",children=[
            dcc.Dropdown(df.term.unique(),value=["covid-19"],multi=True,id="search-bar-form",persistence=True,persistence_type="session"),
            html.Div([
                html.H4("Paramètres"),
                dbc.Switch(label="Diagramme à barre ?",value=False,id="bar-plot-switch")
            ],id="parameters")
            
        ]),
        html.Div([
            dbc.Spinner(
                [dcc.Graph(figure={},id="plot-keywords-bar")],color="danger", type="grow"
            )
        ],id="plot")
    ])
],className="container",style={"font-family":"'Open Sans', sans-serif"})

@app.callback(inputs=[Input(component_id="search-bar-form",component_property="value"),
                      Input(component_id="bar-plot-switch",component_property="value")],
              output=Output(component_id="plot-keywords-bar",component_property="figure"))
def update_bar_plot(values,is_bar_plot):
    return generate_bar_plot(df,values,is_bar_plot)

if __name__ == '__main__':
    app.run_server(debug=True)