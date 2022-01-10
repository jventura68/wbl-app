import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from math import log, floor


def human_format(number, decimals=0):
    if np.isnan(number):
        return "-"
    units = ['', 'm', 'M', 'mM', 'B', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    number = round(number / k**magnitude, decimals)
    if int(number)==number:
        return '%.0f%s' % (number, units[magnitude])
    else:
        return '%.2f%s' % (number, units[magnitude])

df = pd.read_csv('data/wbl_regime.csv')
df['Mujeres'] = df.mujeres.apply(human_format)
df['Hombres'] = df.hombres.apply(human_format)
df.rename({"reportyr":"Año"}, axis=1, inplace=True)
df = df[df["Año"]<2021]

# Read comments on indicators
def get_ind_comments():
    with open('data/indicadores.md') as f:
        data = f.read()
    for i, ind in enumerate(data.split('### ')):
        if i == 0:
            continue
        first_newline = ind.find('\n')+1
        key = ind[:first_newline].strip()
        value = ind[first_newline:-1]
        yield (key,value)


indicadores_text = {key:value for key,value in get_ind_comments()}

app = dash.Dash(__name__)
server = app.server

markdown_text = """
# WBL Index
[**(Women, Business and the Law)**](https://wbl.worldbank.org/en/wbl). 
Este índice valora  entre 0 y 100 el trato igualitario que recibe
la mujer en las leyes y regulaciones de los 190 países analizados. 
Incluye 9 indicadores que valoran distintos aspectos que afectan a 
la igualdad entre hombres y mujeres
"""
box_style = {"border": "1px solid #000", "borderRadius":5}

check_gobiernos = html.Div([
            html.P("Gobiernos:"),
            dcc.Checklist(
                id='gobiernos',
                options=[
                    {'label': 'Democráticos', 'value': 'D'},
                    {'label': 'No elegidos', 'value': 'N'}
                ],
                value=['D', 'N']
            )
            ], style=box_style
        )

check_incoming = html.Div([
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
                )
            ], style=box_style
        )

indicadores = [
                    {'label': 'General', 'value':'WBL INDEX'},
                    {'label': 'Laboral', 'value':'WORKPLACE'},
                    {'label': 'Remuneración', 'value':'PAY'},
                    {'label': 'Movilidad', 'value':'MOBILITY'},
                    {'label': 'Pensiones', 'value':'PENSION'},
                    {'label': 'Matrimonio', 'value':'MARRIAGE'},
                    {'label': 'Bienes', 'value':'ASSETS'},
                    {'label': 'Maternidad', 'value':'PARENTHOOD'},
                    {'label': 'Emprendimiento', 'value':'ENTREPRENEURSHIP'},
                ]

box_style_small = box_style
box_style_small["font-size"]="10px"
panel_indicadores = html.Div([
    html.P("Indicador:"),
    html.Div([
        dcc.RadioItems(
            id='indicador',
            options=indicadores,
            value=indicadores[0]["value"],
            labelStyle={'display': 'block'}
            )
    ],style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        dcc.Markdown(id='indicador_comment', 
                     style={"background-color": "#EEEEEE",
                            "size":"10px",
                            "color":"#777777",
                            "margin": "10px"})
    ],style={'width': '68%', 
             'display': 'inline-block',
             'vertical-align': 'top'
             }),
],style=box_style_small)

panel_izq = html.Div([
    dcc.Markdown(children=markdown_text),
    html.Br(),
    check_gobiernos,
    html.Br(),
    check_incoming,
    html.Br(),
    panel_indicadores
    ],style={'width': '30%', 
             'display': 'inline-block',
             'vertical-align': 'top'
             }
)
panel_der = html.Div([
    dcc.Graph(id="choropleth")
    ],style={'width': '68%', 'display': 'inline-block'}
)

app.layout = html.Div([
    panel_izq,
    panel_der
    ])

@app.callback(
    Output("choropleth", "figure"),
    Output("indicador_comment", "children"),
    Input("gobiernos", "value"),
    Input("income", "value"),
    Input("indicador", "value")
    )

# def update_output_div (gobiernos, income, indicador):
#     return indicadores_text[indicador]

def multi_output(gobiernos, income, indicador):
    df_fil = df

    if len(gobiernos) < 2:
        elected = gobiernos[0]=="D"
        df_fil = df_fil.loc[df.regime_elected==elected]

    if len(income)<4:
        df_fil = df_fil.loc[df.Income.isin(income)]
#WBL INDEX,MOBILITY,PAY,WORKPLACE,MARRIAGE,PARENTHOOD,ENTREPRENEURSHIP,ASSETS,PENSION,regime_elected,Income,region_income,region_elected,income_elected,hombres,mujeres
    df_fil.sort_values("Año", inplace=True)
    fig = px.choropleth(df_fil,
        locations="iso3c", 
        color=indicador,
        hover_name="economy",
        hover_data=["Hombres", "Mujeres"],
        animation_frame="Año",
        color_continuous_scale=['red', 'yellow', 'green'],
        range_color=[0, 100],
        title=str(df_fil["Año"].min())
    )
    fig.update_geos(
        fitbounds="locations",
        projection_type="miller",
        visible=False, 
        showcountries=True, countrycolor="black",
        showland=True, landcolor="#CCCCCC",
        #lataxis={"range":[90,30]}
    )
    sliders=[dict(
        currentvalue={"prefix": "Año: "},
        pad={'t':0}
        # len=0.3,
        # y=1.5, yanchor="bottom",
        # x=0.4, xanchor="left"
    )]

    updatemenus=[dict(
        pad={'t':0}
    )]

    title = dict(
        xanchor='center', x=0.15,
        yanchor='bottom', y=0.40,
        font=dict(
            color='#DDDDDD',
            family='Balto',
            size=60
        )
    )
    fig.update_layout(height=600,
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      title=title,
                      sliders=sliders,
                      updatemenus=updatemenus
                      )

    years = df_fil['Año'].unique()
    for i, frame in enumerate(fig.frames):
        frame.layout.title = str(years[i])
    
    for step in fig.layout.sliders[0].steps:
        step["args"][1]["frame"]["redraw"] = True

    return fig, indicadores_text[indicador]

if __name__ == '__main__':
    app.run_server(debug=True)
