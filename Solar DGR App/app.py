import dash
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import datetime as dt
import plotly.express as px 
from dash import Dash, dcc, html, Input, Output,dash_table,State
from dash import callback
from datetime import date
import base64
import datetime
import io

import plotly.graph_objs as go
from plotly.subplots import make_subplots



app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])

df = pd.read_excel('95 MW Dhuvaran DGR.xlsx',sheet_name='DGR')

df['Date'] = pd.to_datetime(df['Date'], errors='coerce',format='%Y-%m-%d')
desired_format = "%Y-%m-%d"  # Adjust this to your desired format
df['DateColumnFormatted1'] = df['Date'].dt.strftime(desired_format)
df['DateColumnFormatted1'] = pd.to_datetime(df['Date'], errors='coerce',format='%Y-%m-%d')

unique_inverters = df['Inv Name'].unique()
unique_dates = df['Date'].dt.date.unique()

card_df = df.groupby('Inv Name').agg({
    'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean',
    'GII':'mean','GHI':'mean'
})



# Get the minimum and maximum dates from the DataFrame
min_date = df['Date'].min()
max_date = df['Date'].max()

app.layout = html.Div([

    #............................................................................................................
    #............................................................................................................
    ##ALL THE HEADING PARAMETERS.
    ##...........................................................................................................
    ##...........................................................................................................



    dbc.Row(dbc.Col(html.Div(html.H1("95MW Dhuvaran Daily Generation Report",style={'color':'#FFFFFF'}),style={'text-align':'center','backgroundColor':'#6f42c1'})),align='center'),

    dbc.Row([dbc.Col(html.Div(html.H4('O&M Customer: TATA Power',style={'backgroundColor':'#DACA15'},className='py-2')),width=4,style={'text-align':'left'}),
            dbc.Col(
                html.Div([
                html.H4('State :Gujrat',style={'backgroundColor':'#DACA15'},className='py-2')
                        ])
            ,width=4,style={'text-align':'center'}),
            dbc.Col(html.Div(html.H4('O&M Capacity: 75 MWac',style={'backgroundColor':'#DACA15'},className='py-2')),width=4,style={'text-align':'right'})]),

    dbc.Row([
        
        dbc.Col(html.Div([html.H4('Select Start Date',style={'text-align':'left','backgroundColor':'#DACA15'},
                              className='py-2')])),
        dbc.Col(html.Div([
                html.H4('Select End Date',style={'text-align':'center','backgroundColor':'#DACA15'},className='py-2')
                ])),
    dbc.Col(html.Div([html.H4("Select Inv Name",style={'text-align':'right','backgroundColor':'#DACA15'},className='py-2')
                      ]))

    ]),


    #............................................................................................................
    #............................................................................................................
    ##ALL THE DROPDOWN PARAMETERS.
    ##...........................................................................................................
    ##...........................................................................................................



    dbc.Row([
        dbc.Col(html.Div([
                    dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=min(unique_dates),  # Set minimum allowed date
            max_date_allowed=max(unique_dates),  # Set maximum allowed date
            initial_visible_month=min(unique_dates),  # Set initial month to display
            date=min(unique_dates)  # Set initial selected date
            )
            ],style={'border': 'none','padding': '5px','border-radius':'0','text-align':'center','marginBottom': '10px',
                     'backgroundColor':'#DACA15' }),width=4),

            dbc.Col(
                html.Div([
                    dcc.DatePickerSingle(
                    id='end-date-picker',
                    min_date_allowed=min(unique_dates),  # Set minimum allowed date
                    max_date_allowed=max(unique_dates),  # Set maximum allowed date
                    initial_visible_month=max(unique_dates),  # Set initial month to display
                    date=max(unique_dates))
                ],style={'border': 'none','padding': '5px','border-radius':'0','text-align':'center',
                         'marginBottom': '10px','backgroundColor':'#DACA15' }),width=4
            ),

        dbc.Col(html.Div(
                dcc.Dropdown(
            id='inverter-dropdown',
            multi=True,
            options=[{'label': inv, 'value': inv} for inv in unique_inverters],  # Default value
            placeholder="Select an Inverter"
    ),style={'border': 'none','padding': '10px','border-radius':'0','marginBottom': '10px',
             'backgroundColor':'#DACA15' }
        ),width=4)
    ],align='center'),

    

    #............................................................................................................
    #............................................................................................................
    ##ALL THE CARD PARAMETERS.
    ##...........................................................................................................
    ##...........................................................................................................


    dbc.Row([
        dbc.Col(html.Div(id='predicted-irr')),

        dbc.Col(html.Div(id='predicted-gen')),

        dbc.Col(html.Div(id='base-gen1')),

        dbc.Col(html.Div(id='predicted-pr')),

        dbc.Col(html.Div(id='plant-availability'))
    ],align='start',className='pb-2'),
    
    dbc.Row([
        dbc.Col(html.Div(id='actual-irr')),

        dbc.Col(html.Div(id='actual-gen')),

        dbc.Col(html.Div(id='net-gen')),

        dbc.Col(html.Div(id='actual-pr')),

        dbc.Col(html.Div(id='grid-availability'))
    ],align='center',className='pb-2'),

    dbc.Row([
        dbc.Col(html.Div(id='delta-gii')),

        dbc.Col(html.Div(id='delta-gen1')),

        dbc.Col(html.Div(id='delta-base1')),

        dbc.Col(html.Div(id='delta-pr1')),

        dbc.Col(html.Div(dbc.Card(
            dbc.CardBody([
            html.H4("DC Capacity", className="card-title"),
            html.H6("MWh", className="card-subtitle"),
            html.P(
                "95MWp",
                className="card-text",
            )
            ]),style={'background-color':'lightblue'}
        )))
    ],align='end',className='pb-2'),

    dbc.Row([
        dbc.Col(
            html.Div([
                html.H2('Inv Wise PR% & PLF%')
            ],style={'text-align':'center','background-color':'lightblue','padding': '20px','marginBottom':'20px',
                    'marginTop':'20px' })
        )
    ],align='center'),

    dbc.Row([
            dbc.Col(
                html.Div([dcc.Graph(id='line-chart')],style={'padding': '0px'})
            )
            ]),

    dbc.Row([
            dbc.Col(
                html.Div([
                    dash_table.DataTable(data=df.to_dict('records'),
                         page_size=20,
                         style_cell={"background-color": "lightgrey", "border": "solid 1px white", "color": "black", "font-size": "11px", "text-align": "left"},
                         style_header={"background-color": "dodgerblue", "font-weight": "bold", "color": "white", "padding": "10px", "font-size": "18px"},
                        )
                ])
            )
    ])

        
    
],className='mx-2')


##.......................................................................................................
##Alll the callbacks starts here.........................................................................
##.......................................................................................................


#Predicted Irr Callback

@app.callback(
        Output('predicted-irr','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'sum',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean',
                'GII':'mean','GHI':'mean'}).reset_index()
    
    predicted_irr = np.round(((filtered_df2['Budget Irradiation (KWh/m2)'].sum())/(np.mean(df['Inv Name'].nunique()))),2)

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Predicted Irr.", className="card-title"),
            html.H6("KWh/m2", className="card-subtitle"),
            html.P(
                predicted_irr,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#Predicted Gen. Callback

@app.callback(
        Output('predicted-gen','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'sum','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean',
                'GII':'mean','GHI':'mean'}).reset_index()
    
    predicted_gen = np.round(((filtered_df2['Guranteed Generation for this month (KWh)'].sum())/(1000*np.mean(df['Inv Name'].nunique()))),2)

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Predicted Gen.", className="card-title"),
            html.H6("MWh", className="card-subtitle"),
            html.P(
                predicted_gen,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

##Base Gen. Callback

@app.callback(
        Output('base-gen1','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'sum','Generation Delta in KWh':'mean',
                'GII':'mean','GHI':'mean'}).reset_index()
    
    base_gen = np.round(np.round(filtered_df2['Base Generation for a day (KWh)'].sum(),2)/(1000*np.mean(df['Inv Name'].nunique())),2)

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Base Gen.", className="card-title"),
            html.H6("MWh", className="card-subtitle"),
            html.P(
                base_gen,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

##Predicted PR Callback..

@app.callback(
        Output('predicted-pr','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean',
                'GII':'mean','GHI':'mean'}).reset_index()
    
    predicted_pr = np.round(filtered_df2['Predicted PR%'].mean(),2)*100

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Predicted PR%", className="card-title"),
            html.H6("Percentage", className="card-subtitle"),
            html.P(
                predicted_pr,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#plant availability callback

@app.callback(
        Output('plant-availability','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean',
                'GII':'mean','GHI':'mean'}).reset_index()
    
    plant_availability = np.round(filtered_df2['Plant Availability'].mean(),2)*100

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Plant Availability%", className="card-title"),
            html.H6("Percentage", className="card-subtitle"),
            html.P(
                plant_availability,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#Actual Irr. Callback

@app.callback(
        Output('actual-irr','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean',
                'GII':'sum','GHI':'mean'}).reset_index()
    
    actual_irr = np.round((filtered_df2['GII'].sum())/(np.mean(df['Inv Name'].nunique())),2)

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Actual Irr.", className="card-title"),
            html.H6("KWh/m2", className="card-subtitle"),
            html.P(
                actual_irr,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#Actual Gen. Callback.....................

@app.callback(
        Output('actual-gen','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'sum',
                'GII':'mean','GHI':'mean'}).reset_index()
    
    actual_gen = np.round((filtered_df2['NET Generation in KWh'].sum())/(1000*np.mean(df['Inv Name'].nunique())),2)

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Actual Gen.", className="card-title"),
            html.H6("MWh", className="card-subtitle"),
            html.P(
                actual_gen,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#Net Gen. Callback

@app.callback(
        Output('net-gen','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'sum',
                'GII':'mean','GHI':'mean'}).reset_index()
    
    net_gen = np.round((filtered_df2['NET Generation in KWh'].sum(),2)/(1000*np.mean(df['Inv Name'].nunique())),2)

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Net Gen.", className="card-title"),
            html.H6("MWh", className="card-subtitle"),
            html.P(
                net_gen,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#Actual PR% Callback....................

@app.callback(
        Output('actual-pr','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'sum',
                'GII':'mean','GHI':'mean'}).reset_index()
    
    actual_pr = np.round(filtered_df2['PR% W.R.T GII (KWh/m2)'].mean(),2)*100

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Actual PR%", className="card-title"),
            html.H6("Percentage", className="card-subtitle"),
            html.P(
                actual_pr,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]


#Grid Availability Callback.............................................

@app.callback(
        Output('grid-availability','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'mean',
    'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'sum',
                'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    
    grid_avail = np.round(filtered_df2['Grid Availability'].mean(),2)*100

    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Grid Availability%", className="card-title"),
            html.H6("Percentage", className="card-subtitle"),
            html.P(
                grid_avail,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#Delta GII Callback...............................

@app.callback(
        Output('delta-gii','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'mean',
    'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'sum',
                'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    
    delta_gii = np.round((((np.round(filtered_df2['GII'].sum(),2)/(np.mean(df['Inv Name'].nunique())))-(np.round(filtered_df2['Budget Irradiation (KWh/m2)'].sum(),2)/(np.mean(df['Inv Name'].nunique()))))/(np.round(filtered_df2['Budget Irradiation (KWh/m2)'].sum(),2)/(np.mean(df['Inv Name'].nunique()))))*100,2)




    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Delta GII%", className="card-title"),
            html.H6("Percentage", className="card-subtitle"),
            html.P(
                delta_gii,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#Delta Gen (Predicted)........................................

@app.callback(
        Output('delta-gen1','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'mean',
    'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'sum','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'sum',
                'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    
    delta_gen = np.round((((np.round(filtered_df2['NET Generation in KWh'].sum(),2)/(np.mean(df['Inv Name'].nunique())))-(np.round(filtered_df2['Guranteed Generation for this month (KWh)'].sum(),2)/(np.mean(df['Inv Name'].nunique()))))/(np.round(filtered_df2['Guranteed Generation for this month (KWh)'].sum(),2)/(np.mean(df['Inv Name'].nunique()))))*100,2)




    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Delta Gen%", className="card-title"),
            html.H6("Percentage", className="card-subtitle"),
            html.P(
                delta_gen,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]


#Callback for Delta Base Gen...............................

@app.callback(
        Output('delta-base1','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'mean',
    'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'sum','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'sum','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'sum',
                'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    
    delta_gen = np.round((((np.round(filtered_df2['NET Generation in KWh'].sum(),2)/(np.mean(df['Inv Name'].nunique())))-(np.round(filtered_df2['Base Generation for a day (KWh)'].sum(),2)/(np.mean(df['Inv Name'].nunique()))))/(np.round(filtered_df2['Base Generation for a day (KWh)'].sum(),2)/(np.mean(df['Inv Name'].nunique()))))*100,2)




    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Delta Base Gen%", className="card-title"),
            html.H6("Percentage", className="card-subtitle"),
            html.P(
                delta_gen,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]

#Delta PR%......................................

@app.callback(
        Output('delta-pr1','children'),
        [
            Input('start-date-picker', 'date'),
            Input('end-date-picker', 'date'),
            Input('inverter-dropdown', 'value')
        ]
)

def update_card(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'mean',
    'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'sum','Budget Irradiation (KWh/m2)':'mean',
                'Base Generation for a day (KWh)':'sum','Generation Delta in KWh':'mean','Predicted PR%':'mean','Plant Availability':'mean','NET Generation in KWh':'sum',
                'GII':'mean','GHI':'mean','Grid Availability':'mean'}).reset_index()
    
    delta_pr = np.round((((np.round(filtered_df2['PR% W.R.T GII (KWh/m2)'].mean(),2)/(np.mean(df['Inv Name'].nunique())))-(np.round(filtered_df2['Predicted PR%'].mean(),2)/(np.mean(df['Inv Name'].nunique()))))/(np.round(filtered_df2['Predicted PR%'].mean(),2)/(np.mean(df['Inv Name'].nunique()))))*100,2)




    return [
        dbc.Card(
            dbc.CardBody([
            html.H4("Delta PR%", className="card-title"),
            html.H6("Percentage", className="card-subtitle"),
            html.P(
                delta_pr,
                className="card-text",
            ),
            ])
        ,color="success", outline=True,style={'background-color':'lightblue'})

    ]




# Callback to update the line chart based on the selected inverter, date range, and category
@app.callback(
    Output('line-chart', 'figure'),
    [Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date'),
     Input('inverter-dropdown', 'value')])


def update_graphs(start_date_str, end_date_str,selected_inv):
    start_date_str = start_date_str[0:10]
    end_date_str = end_date_str[0:10]
    start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = dt.strptime(end_date_str, '%Y-%m-%d').date()


    filtered_df = df[(df['DateColumnFormatted1'].dt.date >= start_date) & (df['DateColumnFormatted1'].dt.date <= end_date)]
    if selected_inv:  # Check if inverter names are selected
        if isinstance(selected_inv, str):  # Convert single string to a list
            selected_inv = [selected_inv]
        filtered_df = filtered_df[filtered_df['Inv Name'].isin(selected_inv)]

    filtered_df1 = filtered_df.groupby(['Date','Inv Name']).agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean',
                'PR% W.R.T GII (KWh/m2)': 'mean', 'PLF %': 'mean','Inverter Specific Yield':'mean','Guranteed Generation for this month (KWh)':'mean','Budget Irradiation (KWh/m2)':'mean',
    'Base Generation for a day (KWh)':'mean','Generation Delta in KWh':'mean','Predicted PR%':'mean',
    'GII':'mean','GHI':'mean'}).reset_index()
    filtered_df2 = filtered_df1.groupby('Inv Name').agg({'Inverter PR%': 'mean', 'Inverter PLF%': 'mean','Inverter Specific Yield':'mean','Predicted PR%':'mean'}).reset_index()

        # Updating Chart 1
    fig1 = go.Figure()
    threshold = np.round(filtered_df2['Predicted PR%'].mean()*100,2)  # You can set your desired threshold value

    fig1.add_trace(go.Bar(
        x= filtered_df2['Inv Name'],
        y= np.round(filtered_df2['Inverter PR%']*100,2),
        name='Inv Wise PR%',
        marker_color=['red' if val < threshold else 'skyblue' for val in filtered_df2['Inverter PR%']*100],
        yaxis='y'  # Assign to primary y-axis
    ))

    # Create a line chart
    fig1.add_trace(go.Scatter(
        x= filtered_df2['Inv Name'],
        y= np.round(filtered_df2['Inverter PLF%']*100,2),
        mode='lines+markers',
        name='Inv Wise PLF%',
        line=dict(color='orange', width=2),
        yaxis='y2'  # Assign to secondary y-axis
    ))
    

    # Update layout
    fig1.update_layout(
        title_x=0.5,
        height=600,
        xaxis=dict(title='Inv Name',
                   tickfont=dict(
            size=15
            ),title_font=dict(
                    size=20
            ),
            ),
        yaxis=dict(title='Inv PR%',
                   title_font=dict(
                       size=20
                   ),
                   tickfont=dict(
            size=15
        )),
        yaxis2=dict(
        title='Inv Wise PLF%',
        title_font=dict(
            size=20
        ),
        overlaying='y',
        side='right',
        tickfont=dict(
            size=15
        )),
        legend=dict(
            x=0.35,
            y=1.5,
            traceorder='normal',
            orientation='h',  # 'h' for horizontal, 'v' for vertical
            font=dict(
                size=30
            )
        )
    )

    

    return fig1



    


if __name__ == "__main__":
    app.run_server(debug=True)