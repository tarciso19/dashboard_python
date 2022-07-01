from dash import html, callback, dcc
from dash.dependencies import Input, Output
from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime

app = JupyterDash(external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)

# Data import
dados = pd.read_csv("Python_DashBoard/data/data.txt", delimiter=';')

times = dados['Mandante'].str.lower().unique().tolist()
estadios = dados['Arena'].str.lower().unique().tolist()
anos = dados['Data'].apply(lambda x: datetime.strptime(x,'%d/%m/%Y').year).unique().tolist()
dias = dados['Dia'].str.lower().unique().tolist()
estados = dados['Estado Mandante'].unique().tolist()

########################## APP ############################
app.layout = html.Div(children=[

    # Main Area
    html.Div(id='main-area',
    children=[
        # side bar
        html.Div(id='side-bar', children=[
            # Header
            html.Div(id='header',
            children=[
                html.Div([html.H1('BRASILEIRÃO'),html.H4('Data Science')]), # main title
                html.Div(html.Img(src="assets/logo.png",style={'height':'100%', 'width':'80%'})), # ford logo
                ]),
            # Input data area
            html.Div(id='input-area',
            children=[
                html.H6('Times', style = {'margin-top':'-11.5px'}),
                html.Div(dcc.Dropdown(id='times', className='dropdown', options = times, multi=True)),
                html.H6('Anos'),
                html.Div(dcc.RangeSlider(2003,2021,1,marks=None, value=[2003,2021], tooltip={"placement": "bottom", "always_visible": True}, count=3,id='anos'))
            ])
        ]),

        # Where is the data from
        html.Div(id='label-area', children=[
            html.H4('ANÁLISE DE DADOS DO CAMPEONATO BRASILEIRO (2003-2021)')
        ]),
        
        # plot and table area
        html.Div(id='plots-area', children=[ 

            # pie chart for forums
            html.Div(className='pie', children=[
                html.Div(className='plot-title', children=['Gol em casa x Gol fora']),
                html.Div(id='pie-chart-gols-mandantes-visitante')
            ]),

            # pie chart for users
            html.Div(id='bar', children=[
                html.Div(className='plot-title', children=['Distribuição da quantidade de gols por ano e condição de jogo']),
                html.Div(id='bar-chart')
            ])
        ]),

        html.Div(className='clear'),
        html.Div(id='pareto', children=[
            html.Div(className='plot-title', children=['Distribuição da quantidade de gols por time e condição de jogo']),
            html.Div(id='pareto-chart')
        ])
    ])
])


# Pie chart para divisão de gols entre mandante e visitante
@callback(Output('pie-chart-gols-mandantes-visitante', 'children'), Input('times', 'value'),Input('anos', 'value'))
def insert_pie_chart(times, years):

    # Filtrando pelo ano
    selected_years = list(range(years[0],years[-1]+1,1))
    df_ano = dados[dados['Data'].apply(lambda x: datetime.strptime(x,'%d/%m/%Y').year in selected_years)]

    if times is not None:

        mandantes = df_ano[df_ano['Mandante'].apply(lambda x: x.lower()).isin(times)]['Mandante Placar'].sum()
        visitantes = df_ano[df_ano['Visitante'].apply(lambda x: x.lower()).isin(times)]['Visitante Placar'].sum()

    else:

        mandantes = df_ano['Mandante Placar'].sum()
        visitantes = df_ano['Visitante Placar'].sum()

    d = {'Mandantes':mandantes, 'Visitantes':visitantes}
    df = pd.DataFrame(data=d.items(), columns=['Condicao', 'Soma'])
    fig = px.pie(df, values='Soma', names='Condicao', template="plotly_dark")
    fig.update_layout(legend={'orientation':'h'})
              
    return dcc.Graph(figure=fig)

# Calling pareto plot
@callback(Output('bar-chart', 'children'), Input('times', 'value'), Input('anos', 'value'))
def insert_pareto_chart(times,years):

    selected_years = list(range(years[0],years[-1]+1,1))

    if times is not None:
        dados_pareto = pd.concat([dados[dados['Mandante'].apply(lambda x: x.lower()).isin(times)],dados[dados['Visitante'].apply(lambda x: x.lower()).isin(times)]])
    else:
        dados_pareto = dados
    
    dados_pareto['Ano'] = dados_pareto['Data'].apply(lambda x: datetime.strptime(x,'%d/%m/%Y').year)
    soma = []; condicao = []; anos =[]
    for ano in selected_years:
        soma.append(dados_pareto[dados_pareto['Ano'] == ano]['Mandante Placar'].sum())
        condicao.append('mandante')
        anos.append(ano)
        soma.append(dados_pareto[dados_pareto['Ano'] == ano]['Visitante Placar'].sum())
        condicao.append('visitante')
        anos.append(ano)

    df = pd.DataFrame(data=zip(anos,condicao,soma), columns=['Ano', 'Condição', 'Gols'])

    fig = px.bar(df, x="Ano", y="Gols", color="Condição",template='plotly_dark',barmode="group")

    return dcc.Graph(figure=fig)

# Calling pareto plot
@callback(Output('pareto-chart', 'children'), Input('times', 'value'), Input('anos', 'value'))
def insert_pareto_chart(times,years):

    if times is None:

        # Filtrando pelo ano
        selected_years = list(range(years[0],years[-1]+1,1))
        dados_ano = dados[dados['Data'].apply(lambda x: datetime.strptime(x,'%d/%m/%Y').year in selected_years)]

        # Filtrando pelo time
        if times is not None:
            dados_ano_time = pd.concat([dados_ano[dados_ano['Mandante'].apply(lambda x: x.lower()).isin(times)],\
                dados_ano[dados_ano['Visitante'].apply(lambda x: x.lower()).isin(times)]])
        else:
            dados_ano_time = dados_ano
        
        soma = []; condicao = []; time_list =[]
        for time in dados_ano_time['Mandante'].str.lower().unique().tolist():
            soma.append(dados_ano_time[dados_ano_time['Mandante'].str.lower() == time]['Mandante Placar'].sum())
            condicao.append('mandante')
            time_list.append(time)
            soma.append(dados_ano_time[dados_ano_time['Visitante'].str.lower() == time]['Visitante Placar'].sum())
            condicao.append('visitante')
            time_list.append(time)
        
        df = pd.DataFrame(data=zip(time_list,condicao,soma), columns=['Time', 'Condição', 'Gols'])

        df.sort_values('Gols', ascending=False, inplace=True)
        df['cumperc'] = df['Gols'].cumsum()/df['Gols'].sum()

        fig =px.bar(df, x='Time', y='Gols', color="Condição",template='plotly_dark',barmode="group")

        return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True)
