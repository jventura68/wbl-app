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
app.title = "WBL Index - José Ventura"
server = app.server

felicidad_text="""
# Práctica de visualización de datos

## Aplicación y código fuente
* __url publicación app__: https://wbl-app.herokuapp.com/
* __repositorio github__: https://github.com/jventura68/wbl-app

## Herramientas de visualización utilizadas

* **Flourish**  
  Se utilizó en las anteriores prácticas y en las primeras visualizaciones
  realizadas para esta, finalmente se abandona, es una buena herramienta
  para un primer esbozo, pero las posibilidades de personalización son pocas
  y la utilización de los gráficos en páginas web no es sencilla.
* **Plotly**  
  Elaboración de gráficos y mapas interactivos. Requiere inversión de tiempo
  en los primeros momentos, pero los resultados, la personalización e integración
  son perfectas.
* **Dash**  
  Herramienta elegida para la construcción del cuadro de mando de la aplicación.
  Permite una gran configuración de los componentes y tiene una integración perfecta
  con Plotly

# Investigación y visualización de datos
## Índice de felicidad

### ¿Qué preguntas nos hacemos?
Después de un periodo de noticias y situaciones apocalípticas, parece que 
una buena forma de romper la tendencia negativa es analizar la felicidad 
y cómo ha cambiado el mundo en los últimos años. El fín último era contestar a 
la pregunta: **¿El mundo puede ser feliz si la mitad de la población (Mujeres) 
no tienen libertad?**

No tenemos suficientes datos para contestar esta pregunta, en la 
[PEC3](https://public.flourish.studio/story/1067848/) analizé algunos aspectos
de la felicidad en el mundo, pero no se analizó la correlación entre la felicidad
y la libertad de las mujeres.  

### ¿Cómo medimos el índice de libertad de la mujer?
[El Banco Mundial](https://www.bancomundial.org/es/home) lanza muchas iniciativas que 
ponen a disposición pública datos socio-económicos de interés para investigadores. Una
de estas iniciativas es el índice [WBL (Women, Business and the Law)](https://wbl.worldbank.org/en/wbl)

Como punto de partida se analiza la correlación entre este índice con el índice de
felicidad (expuesto en la [PEC3](https://public.flourish.studio/story/1067848/)) y
con la Renta per cápita. A continuación mostramos los dos gráficos:
"""
header_text = """
## WBL Index
[**(Women, Business and the Law)**](https://wbl.worldbank.org/en/wbl). 
Este índice valora  entre 0 y 100 el trato igualitario que recibe
la mujer en las leyes y regulaciones de los 190 países analizados. 
Incluye 9 indicadores que valoran distintos aspectos que afectan a 
la igualdad entre hombres y mujeres
"""
sources_text="""
#### Fuentes:
* **Índice de felicidad:** Helliwell, John F., Richard Layard, Jeffrey 
  Sachs, and Jan-Emmanuel De Neve, eds. 2021. World Happiness Report 2021. 
  New York: Sustainable Development Solutions Network.
* **WBL Index:** World Bank. 2021. Women, Business and the Law 2021. 
  Washington, DC: World Bank. © World Bank. 
  https://openknowledge.worldbank.org/handle/10986/35094 
  License: CC BY 3.0 IGO.
* **Régimen de gobierno:** Bell, Curtis, Besaw, Clayton., Frank, 
  Matthew. 2021. The Rulers, Elections, and Irregular Governance
  (REIGN) Dataset. Broomfield, CO: One Earth Future. Available 
  at https://oefdatascience.github.io/REIGN.github.io/
"""
panel_correlacion = html.Div([
    html.Div([
        dcc.Graph(id="corr_gdp")
    ],style={'width': '50%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id="corr_life")
    ],style={'width': '50%', 'display': 'inline-block'
             }),
])

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
    html.Div([
        html.P("Indicador:"),
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
             'vertical-align': 'top',
             'font-size':'12px',
             }),
],style=box_style)

panel_izq = html.Div([
    dcc.Markdown(children=header_text),
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
    dcc.Markdown(children=felicidad_text),
    panel_correlacion,
    panel_izq,
    panel_der,
    dcc.Markdown(children=sources_text)
    ])

felicidad = pd.read_csv('data/data_to_gdp_felicidad_wbl.csv')
def graph_corr (df=felicidad, x="Life ladder", 
                              xlabel="Índice de felicidad",
                              y="WBL index",
                              ylabel="Índice WBL"):
    return px.scatter(
        df, y=y, x=x, 
        title="Gráfico de dispersión",
        hover_name = "Country",
        labels={x: xlabel,
                y: ylabel},
        animation_frame="Year", #color="Region",
        opacity=0.4,
        trendline_color_override="red", trendline="lowess")


@app.callback(
    Output("corr_gdp", "figure"),
    Output("corr_life", "figure"),
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
        if len(gobiernos)<1:
            df_fil = df_fil.iloc[:1][df_fil['Año']>3000]
        else:
            elected = gobiernos[0]=="D"
            df_fil = df_fil.loc[df.regime_elected==elected]

    if len(income)<4:
        df_fil = df_fil.loc[df.Income.isin(income)]

    df_fil.sort_values("Año", inplace=True)

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
    label_ind = ""
    for ind in indicadores:
        if ind['value']==indicador:
            label_ind = ind['label']


    if df_fil.shape[0]==0:
        mapa = px.choropleth(df_fil,
            locations="iso3c"
            )
    else:
        mapa = px.choropleth(df_fil,
            locations="iso3c", 
            color=indicador,
            hover_name="economy",
            hover_data=["Hombres", "Mujeres"],
            animation_frame="Año",
            color_continuous_scale=['purple','red', 'yellow', 'green'],
            range_color=[0, 100],
            title=str(df_fil["Año"].min())
            )
    mapa.update_geos(
        fitbounds="locations",
        projection_type="natural earth",
        visible=False, 
        showcountries=True, countrycolor="black",
        showland=True, landcolor="#CCCCCC",
        #lataxis={"range":[90,30]}
    )


    mapa.update_layout(height=600,
                      margin={"r": 0, "t": 0, "l": 0, "b": 0},
                      title=title,
                      coloraxis_colorbar=dict(
                          title=label_ind
                      ),
                      sliders=sliders,
                      updatemenus=updatemenus
                      )

    years = df_fil['Año'].unique()
    for i, frame in enumerate(mapa.frames):
        frame.layout.title = str(years[i])
    
    for step in mapa.layout.sliders[0].steps:
        step["args"][1]["frame"]["redraw"] = True

    return (graph_corr(), graph_corr(x="GDPpc", xlabel="Renta per cápita"), 
            mapa, indicadores_text[indicador]
    )

if __name__ == '__main__':
    app.run_server(debug=True)
