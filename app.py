import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv('data/wbl_regime.csv')

app = dash.Dash(__name__)
server = app.server

markdown_text = """
## WBL Index
Es un índice que valora las leyes y regulaciones de 190 países y cómo afectan a las mujeres.
Contiene varios indicadores que valoran la igualdad de estas leyes entre hombres y mujeres.
"""


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
            ], style={"border": "1px solid #000"}
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
            ], style={"border": "1px solid #000"}
        )

indicadores = [
                    {'label': 'General', 'value':'WBL INDEX'},
                    {'label': 'Lugar de Trabajo', 'value':'WORKPLACE'},
                    {'label': 'Pagos', 'value':'PAY'},
                    {'label': 'Movilidad', 'value':'MOBILITY'},
                    {'label': 'Pensiones', 'value':'PENSION'},
                    {'label': 'Matrimonio', 'value':'MARRIAGE'},
                    {'label': 'Posesiones', 'value':'ASSETS'},
                    {'label': 'Maternidad', 'value':'PARENTHOOD'},
                    {'label': 'Emprendimiento', 'value':'ENTREPRENEURSHIP'},
                ]
indicadores_text = {
    'WBL INDEX': """
    __Es la media de las puntuaciones obtenidas en los índices de:__
    * Lugar de trabajo
    * Pagos
    * Movilidad
    * Pensiones
    * Matrimonio
    * Posesiones
    * Maternidad
    * Emprendimiento
    """,
    'WORKPLACE': """
    * ¿Puede una mujer .... de igual forma que un hombre?
      * Conseguir trabajo
      * Acceso por ley a los trabajos
    * ¿Existen leyes contra el acoso sexual en el trabajo?
    * ¿Se castiga el acoso sexual en el trabajo?
    """,
    'PAY': """
    * ¿La ley obliga a remunerar por igual a mujeres y hombres?
    * ¿Puede una mujer .... de igual forma que un hombre?
      * Trabajar por la noche
      * Conseguir trabajos considerados peligrosos
      * Trabajar en la industria
    """,
    'MOBILITY': """
    * ¿Puede una mujer realizar estas operaciones igual que un hombre?  
      * Obtener un pasaporte
      * Viajar al extranjero
      * Salir de su hogar
      * Elegir dónde vivir
    """,
    'PENSION': """
    * ¿Son iguales para mujeres y hombres:
      * La edad de jubilación para pensión total
      * La edad de jubilación para pensión parcial
    * ¿La edad de jubilación igual por ley para hombre y mujeres?
    * ¿Computan como beneficios para la pensión el cuidado de hijos?
    """,
    'MARRIAGE': """
    * Por ley, ¿la mujer casada debe obeceder al marido?
    * ¿Hay leyes para la violencia doméstica?
    * ¿Las mujeres están en las mismas condiciones que un hombre para...?:
      * Ser cabeza de familia
      * Pedir el divorcio
      * Volver a casarse
    """,
    'ASSETS': """
    * ¿Tienen las mujeres y hombres los mismos derechos para ...?:
      * Poseer bienes inmuebles
      * Heredar de sus padres
      * Heredar por viudedad
      * Gestionar los bienes gananciales del matrimonio
    * ¿Reconocen las leyes el valor del trabajo en el hogar?
    """,
    'PARENTHOOD': """
    * ¿Existen al menos 14 semanas de baja remuneradas?
    * _Se incluye valoración tiempo de baja para el padre y la madre_
    * El gobierno es responsable del 100% de la baja
    * ¿Los padres tienen baja remunerada?
    * ¿Está prohibido el despido de trabajadoras embarazadas?
    """,
    'ENTREPRENEURSHIP': """
    * ¿Puede una mujer realizar estas operaciones igual que un hombre?  
      * Firmar un contrato
      * Crear una empresa
      * Abrir una cuenta bancaria
      * Acceso al crédito
    """,
}

indicador_radio = html.Div(
      [
        html.P("Indicador:"),
        dcc.RadioItems(
            id='indicador',
            options=indicadores,
            value=indicadores[0]["value"]
            ),
        dcc.Markdown(id='indicador_comment', 
                     style={"background-color": "#EEEEEE", 
                            "color":"#777777",
                            "margin": "10px"})
      ], 
      style={"border": "1px solid #000"}
    )

panel_izq = html.Div([
    check_gobiernos,
    check_incoming,
    indicador_radio
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
    dcc.Markdown(children=markdown_text),
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

    fig = px.choropleth(df_fil, 
                    locations="iso3c", 
                    color=indicador,
                    hover_name="economy",
                    animation_frame="reportyr",
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[0, 100]
    )
    fig.update_geos(
        projection_type="natural earth",
        visible=False, 
        showcountries=True, countrycolor="black",
        showland=True, landcolor="#CCCCCC",
        lataxis={"range":[90,-55]}
    )
    fig.update_layout(#height: 500,
                      margin={"r": 0, "t": 20, "l": 20, "b": 0},
                      title={'xanchor':'center', 'x':0.5,
                             'yanchor':'bottom', 'y':0.2,
                             'font':{
                                 'color':'#DDDDDD',
                                 'family':'Balto',
                                 'size':90
                             }
                      })

    years = df_fil.reportyr.unique()
    for i, frame in enumerate(fig.frames):
        frame.layout.title = str(years[i])
    
    for step in fig.layout.sliders[0].steps:
        step["args"][1]["frame"]["redraw"] = True

    return fig, indicadores_text[indicador]

if __name__ == '__main__':
    app.run_server(debug=True)
