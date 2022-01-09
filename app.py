import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv('data/wbl_regime.csv')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.P("Gobiernos:"),
    dcc.Checklist(
        id='gobiernos',
        options=[
            {'label': 'Democráticos', 'value': 'D'},
            {'label': 'No elegidos', 'value': 'N'}
        ],
        value=['D', 'N']
    ),
    html.P("PIB:"),
    dcc.Checklist(
        id='income',
        options=[
            {'label': 'Bajo', 'value':'Low'},
            {'label': 'Medio Bajo', 'value':'Low-Middle'},
            {'label': 'Medio Alto', 'value':'Middle-High'},
            {'label': 'Alto', 'value':'High'},
        ],
        value=['Low', 'Low-Middle', 'Middle-High', 'High']
    ),
    dcc.Graph(id="choropleth"),
])

@app.callback(
    Output("choropleth", "figure"), 
    [Input("gobiernos", "value"),
     Input("income", "value")])

def display_choropleth(gobiernos, income):
    df_fil = df

    if len(gobiernos) < 2:
        elected = gobiernos[0]=="D"
        df_fil = df_fil.loc[df.regime_elected==elected]

    if len(income)<4:
        df_fil = df_fil.loc[df.Income.isin(income)]

    fig = px.choropleth(df_fil, 
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

if __name__ == '__main__':
    app.run_server(debug=True)
