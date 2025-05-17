# Importar paquetes necesarios
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from datetime import datetime

# Cargar datos
df = pd.read_csv("Superservicios.csv")

# Limpieza y preparación de datos
df['ANIO'] = pd.to_numeric(df['ANIO'], errors='coerce')
df['MES'] = pd.to_numeric(df['MES'], errors='coerce')
df = df.dropna(subset=['ANIO', 'MES'])

# Convertir a fecha para facilitar el manejo de tiempo
df['FECHA'] = pd.to_datetime(df['ANIO'].astype(str) + '-' + df['MES'].astype(str) + '-01')

# Calcular semestre
df['SEMESTRE'] = df['MES'].apply(lambda x: 1 if x <= 6 else 2)

# Valores mínimos y máximos para los sliders
min_year = int(df['ANIO'].min())
max_year = int(df['ANIO'].max())

# Inicializar la aplicación con tema Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

# Opciones para los controles
time_options = [
    {'label': 'Año', 'value': 'ANIO'},
    {'label': 'Mes', 'value': 'MES'},
    {'label': 'Semestre', 'value': 'SEMESTRE'}
]

company_options = [{'label': empresa, 'value': empresa} for empresa in df['EMPRESA'].unique()]
sender_options = [{'label': tipo, 'value': tipo} for tipo in df['TIPO_REMITENTE'].unique()]

# Diseño del tablero
app.layout = dbc.Container([
    # Título principal
    dbc.Row([
        html.H1("Análisis de Transporte de Hidrocarburos", 
                className="text-center text-primary my-4")
    ]),
    
    # Primera fila de gráficos
    dbc.Row([
        # Gráfico de líneas con controles de tiempo
        dbc.Col([
            html.H3("Evolución Mensual de Valores Facturados", className="text-center"),
            dcc.Graph(id='line-chart'),
            html.Div([
                dbc.Label("Seleccionar período:"),
                dbc.RadioItems(
                    id='time-radio',
                    options=time_options,
                    value='MES',
                    inline=True
                ),
                dbc.Label("Seleccionar rango de años:"),
                dcc.RangeSlider(
                    id='year-slider',
                    min=min_year,
                    max=max_year,
                    step=1,
                    value=[min_year, max_year],
                    marks={str(year): str(year) for year in range(min_year, max_year+1)}
                )
            ], className="p-3 border rounded")
        ], md=6),
        
        # Gráfico de barras con selector de empresa
        dbc.Col([
            html.H3("Comparación por Empresa", className="text-center"),
            dcc.Graph(id='bar-chart'),
            html.Div([
                dbc.Label("Seleccionar empresa:"),
                dcc.Dropdown(
                    id='company-dropdown',
                    options=company_options,
                    value=df['EMPRESA'].unique()[0],
                    multi=True
                ),
                dbc.Button("Cambiar Orientación", id='orientation-button', 
                          color="primary", className="mt-2")
            ], className="p-3 border rounded")
        ], md=6)
    ], className="mb-4"),
    
    # Segunda fila de gráficos
    dbc.Row([
        # Gráfico de pastel (mostrando ambas empresas sin filtros)
        dbc.Col([
            html.H3("Distribución del Recaudo por ECO entre Empresas", className="text-center"),
            dcc.Graph(id='pie-chart'),
            html.Div([
                dbc.Label("Variable a visualizar:"),
                dbc.RadioItems(
                    id='pie-metric-radio',
                    options=[
                        {'label': 'Recaudo ECO', 'value': 'RECAUDO_POR_ECO_PESOS'},
                        {'label': 'Cantidad Transportada', 'value': 'CANTIDAD_KG'},
                        {'label': 'Valor Facturado', 'value': 'VALOR_FACTURA_PESOS'}
                    ],
                    value='RECAUDO_POR_ECO_PESOS',
                    inline=True
                ),
                dbc.Button("Cambiar Colores", id='color-button', 
                          color="success", className="mt-2")
            ], className="p-3 border rounded")
        ], md=6),
        
        # Gráfico de dispersión
        dbc.Col([
            html.H3("Relación Cantidad vs Valor", className="text-center"),
            dcc.Graph(id='scatter-chart'),
            html.Div([
                dbc.Label("Variable para tamaño de burbujas:"),
                dcc.Dropdown(
                    id='size-dropdown',
                    options=[
                        {'label': 'Valor Factura', 'value': 'VALOR_FACTURA_PESOS'},
                        {'label': 'Cargo Transporte', 'value': 'CARGO_TRANSPORTE_PESOS_KG'},
                        {'label': 'Recaudo ECO', 'value': 'RECAUDO_POR_ECO_PESOS'}
                    ],
                    value='VALOR_FACTURA_PESOS'
                )
            ], className="p-3 border rounded")
        ], md=6)
    ]),
    
    # Pie de página
    dbc.Row([
        dbc.Col([
            html.P("Datos proporcionados por Superservicios", className="text-muted text-center"),
            html.P(f"Última actualización: {datetime.now().strftime('%Y-%m-%d')}", 
                  className="text-muted text-center")
        ], className="mt-4")
    ])
], fluid=True)

# Callbacks para actualizar los gráficos

# Gráfico de líneas
@app.callback(
    Output('line-chart', 'figure'),
    [Input('time-radio', 'value'),
     Input('year-slider', 'value')]
)
def update_line_chart(time_period, year_range):
    filtered_df = df[(df['ANIO'] >= year_range[0]) & (df['ANIO'] <= year_range[1])]
    
    if time_period == 'MES':
        # Agrupar por año y mes para mostrar evolución mensual
        grouped = filtered_df.groupby(['ANIO', 'MES'])['VALOR_FACTURA_PESOS'].sum().reset_index()
        fig = px.line(
            grouped, 
            x='MES', 
            y='VALOR_FACTURA_PESOS', 
            color='ANIO',
            labels={'MES': 'Mes', 'VALOR_FACTURA_PESOS': 'Valor Facturado (COP)'},
            title='Evolución Mensual del Valor Facturado'
        )
    elif time_period == 'SEMESTRE':
        # Agrupar por año y semestre
        grouped = filtered_df.groupby(['ANIO', 'SEMESTRE'])['VALOR_FACTURA_PESOS'].sum().reset_index()
        fig = px.line(
            grouped, 
            x='SEMESTRE', 
            y='VALOR_FACTURA_PESOS', 
            color='ANIO',
            labels={'SEMESTRE': 'Semestre', 'VALOR_FACTURA_PESOS': 'Valor Facturado (COP)'},
            title='Evolución Semestral del Valor Facturado'
        )
    else:
        # Agrupar solo por año
        grouped = filtered_df.groupby('ANIO')['VALOR_FACTURA_PESOS'].sum().reset_index()
        fig = px.line(
            grouped, 
            x='ANIO', 
            y='VALOR_FACTURA_PESOS',
            labels={'ANIO': 'Año', 'VALOR_FACTURA_PESOS': 'Valor Facturado (COP)'},
            title='Evolución Anual del Valor Facturado'
        )
    
    fig.update_layout(transition_duration=500)
    return fig

# Gráfico de barras
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('company-dropdown', 'value'),
     Input('orientation-button', 'n_clicks')]
)
def update_bar_chart(selected_companies, n_clicks):
    if not isinstance(selected_companies, list):
        selected_companies = [selected_companies]
    
    filtered_df = df[df['EMPRESA'].isin(selected_companies)]
    grouped = filtered_df.groupby(['EMPRESA', 'ANIO'])['CANTIDAD_KG'].sum().reset_index()
    
    # Cambiar orientación con el botón
    orientation = 'v' if n_clicks is None or n_clicks % 2 == 0 else 'h'
    
    fig = px.bar(
        grouped,
        x='ANIO' if orientation == 'v' else 'CANTIDAD_KG',
        y='CANTIDAD_KG' if orientation == 'v' else 'ANIO',
        color='EMPRESA',
        barmode='group',
        labels={'CANTIDAD_KG': 'Cantidad Transportada (KG)', 'ANIO': 'Año'},
        title='Cantidad Transportada por Empresa'
    )
    
    fig.update_layout(transition_duration=500)
    return fig

# Gráfico de pastel (mostrando ambas empresas)
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('pie-metric-radio', 'value'),
     Input('color-button', 'n_clicks'),
     Input('year-slider', 'value')]
)
def update_pie_chart(selected_metric, n_clicks, year_range):
    filtered_df = df[(df['ANIO'] >= year_range[0]) & (df['ANIO'] <= year_range[1])]
    grouped = filtered_df.groupby('EMPRESA')[selected_metric].sum().reset_index()
    
    # Cambiar colores con el botón
    if n_clicks is None or n_clicks % 2 == 0:
        color_sequence = px.colors.qualitative.Pastel
    else:
        color_sequence = px.colors.qualitative.Dark2
    
    # Definir etiquetas según la métrica seleccionada
    if selected_metric == 'RECAUDO_POR_ECO_PESOS':
        title = 'Distribución del Recaudo por ECO entre Empresas'
        values_label = 'Recaudo (COP)'
    elif selected_metric == 'CANTIDAD_KG':
        title = 'Distribución de Cantidad Transportada entre Empresas'
        values_label = 'Cantidad (KG)'
    else:
        title = 'Distribución del Valor Facturado entre Empresas'
        values_label = 'Valor (COP)'
    
    fig = px.pie(
        grouped,
        names='EMPRESA',
        values=selected_metric,
        title=title,
        color_discrete_sequence=color_sequence,
        labels={'EMPRESA': 'Empresa', selected_metric: values_label}
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>" +
                      f"{values_label}: %{{value:,}}<br>" +
                      "Porcentaje: %{percent}"
    )
    fig.update_layout(transition_duration=500)
    return fig

# Gráfico de dispersión
@app.callback(
    Output('scatter-chart', 'figure'),
    [Input('size-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_scatter_chart(size_var, year_range):
    filtered_df = df[(df['ANIO'] >= year_range[0]) & (df['ANIO'] <= year_range[1])]
    
    fig = px.scatter(
        filtered_df,
        x='CANTIDAD_KG',
        y='VALOR_FACTURA_PESOS',
        size=size_var,
        color='EMPRESA',
        hover_name='EMPRESA',
        hover_data=['ANIO', 'MES', 'TIPO_REMITENTE'],
        labels={
            'CANTIDAD_KG': 'Cantidad Transportada (KG)',
            'VALOR_FACTURA_PESOS': 'Valor Facturado (COP)',
            'EMPRESA': 'Empresa'
        },
        title='Relación entre Cantidad Transportada y Valor Facturado'
    )
    
    fig.update_layout(transition_duration=500)
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)