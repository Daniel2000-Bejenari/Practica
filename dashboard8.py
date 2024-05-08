import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Încărcați datele
df = pd.read_csv('C:/Users/Dany/Desktop/proiect_practica/bff.csv')

# Conversia coloanei 'Data factura' la format de dată moment
df['Data factura'] = pd.to_datetime(df['Data factura'])

# Inițializați aplicația Dash
app = dash.Dash(__name__)

# Stilizarea paginii folosind CSS
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css']

# Layout-ul aplicației
app.layout = html.Div(className='container', style={'backgroundColor': '#f0f0f0', 'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1(
        className='display-4',
        children='Dashboard de Analiză a Facturilor',
        style={'textAlign': 'center', 'color': '#333333'}
    ),

    html.Div(className='row', children=[
        html.Div(className='col-md-6', children=[
            html.Label('Selectați anul:'),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in df['Data factura'].dt.year.unique()],
                value=df['Data factura'].dt.year.max(),
                className='form-control'
            ),
        ]),

        html.Div(className='col-md-6', children=[
            html.Label('Selectați furnizorul:'),
            dcc.Dropdown(
                id='supplier-dropdown',
                options=[{'label': supplier, 'value': supplier} for supplier in df['Furnizor'].unique()],
                multi=True,
                className='form-control'
            ),
        ]),
    ]),

    html.Div(className='row', children=[
        html.Div(className='col-md-6', children=[
            html.Label('Selectați tipul documentului:'),
            dcc.Dropdown(
                id='doc-type-dropdown',
                options=[{'label': doc_type, 'value': doc_type} for doc_type in df['Tip document'].unique()],
                multi=True,
                className='form-control'
            ),
        ]),

        html.Div(className='col-md-6', children=[
            html.Label('Selectați intervalul de sumă:'),
            dcc.RangeSlider(
                id='sum-range-slider',
                min=df['Suma factura (lei)'].min(),
                max=df['Suma factura (lei)'].max(),
                step=1000,
                marks={i: str(i) for i in range(0, int(df['Suma factura (lei)'].max())+1, 5000)},
                value=[df['Suma factura (lei)'].min(), df['Suma factura (lei)'].max()],
                className='form-control-range'
            ),
        ]),
    ]),

    html.Div(id='data-statistics', style={'color': '#333333'}),

    dcc.Graph(id='bar-chart'),

    dcc.Graph(id='pie-chart'),

    html.Div(id='data-table')
])


# Definirea callback-ului pentru actualizarea statisticilor și graficelor în funcție de filtrele selectate
@app.callback(
    [Output('data-statistics', 'children'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('data-table', 'children')],
    [Input('year-dropdown', 'value'),
     Input('supplier-dropdown', 'value'),
     Input('doc-type-dropdown', 'value'),
     Input('sum-range-slider', 'value')]
)
def update_data(year, suppliers, doc_types, sum_range):
    filtered_df = df[df['Data factura'].dt.year == year]

    if suppliers:
        filtered_df = filtered_df[filtered_df['Furnizor'].isin(suppliers)]

    if doc_types:
        filtered_df = filtered_df[filtered_df['Tip document'].isin(doc_types)]

    filtered_df = filtered_df[(filtered_df['Suma factura (lei)'] >= sum_range[0]) & (filtered_df['Suma factura (lei)'] <= sum_range[1])]

    num_entries = len(filtered_df)
    total_sum = filtered_df['Suma factura (lei)'].sum()
    avg_sum = filtered_df['Suma factura (lei)'].mean()

    statistics_div = html.Div([
        html.Div(f'Număr total de înregistrări: {num_entries}'),
        html.Div(f'Suma totală a facturilor: {total_sum} lei'),
        html.Div(f'Media sumei facturilor: {avg_sum:.2f} lei')
    ])

    bar_chart_fig = px.bar(filtered_df, x='Furnizor', y='Suma factura (lei)', title='Suma facturilor pe furnizor')
    pie_chart_fig = px.pie(filtered_df, names='Furnizor', values='Suma factura (lei)',
                           title='Distribuția sumei facturilor pe furnizor')

    data_table = html.Table(
        # Header
        [html.Tr([html.Th(col) for col in filtered_df.columns])] +
        # Body
        [html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns]) for i in range(min(100, len(filtered_df)))]
    )

    return statistics_div, bar_chart_fig, pie_chart_fig, data_table

# Rulează aplicația Dash
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
