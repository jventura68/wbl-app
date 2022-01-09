import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_excel('data/wbl_regime.csv')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.P("Gobiernos:"),
    dcc.RadioItems(
        id='elected', 
        options=[{'value': 'Democrático', 'label': True},
                  'value': 'No elegido', 'label': False}],
        value=True,
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id="choropleth"),
])

@app.callback(
    Output("choropleth", "figure"), 
    [Input("elected", "value")])
def display_choropleth(elected):
    fig = px.choropleth(df, 
                    locations="iso3c", 
                    color="WBL INDEX",
                    hover_name="economy",
                    animation_frame="reportyr",
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[20, 100]
    )
    fig.update_geos(
        projection_type="natural earth",
        visible=False, 
        showcountries=True, countrycolor="black",
        showland=True, landcolor="#CCCCCC"
    )

    fig.update_layout(height=500, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig

app.run_server(debug=True)
