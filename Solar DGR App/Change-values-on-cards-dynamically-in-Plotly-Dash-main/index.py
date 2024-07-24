import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
url_recovered = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

confirmed = pd.read_csv(url_confirmed)
deaths = pd.read_csv(url_deaths)
recovered = pd.read_csv(url_recovered)

# Unpivot data frames
date1 = confirmed.columns[4:]
total_confirmed = confirmed.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=date1, var_name='date', value_name='confirmed')
date2 = deaths.columns[4:]
total_deaths = deaths.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=date2, var_name='date', value_name='death')
date3 = recovered.columns[4:]
total_recovered = recovered.melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], value_vars=date3, var_name='date', value_name='recovered')

# Merging data frames
covid_data = total_confirmed.merge(right=total_deaths, how='left', on=['Province/State', 'Country/Region', 'date', 'Lat', 'Long'])
covid_data = covid_data.merge(right=total_recovered, how='left', on=['Province/State', 'Country/Region', 'date', 'Lat', 'Long'])

# Converting date column from string to proper date format
covid_data['date'] = pd.to_datetime(covid_data['date'])

# Check how many missing value naN
covid_data.isna().sum()

# Replace naN with 0
covid_data['recovered'] = covid_data['recovered'].fillna(0)

# Calculate new column
covid_data['active'] = covid_data['confirmed'] - covid_data['death'] - covid_data['recovered']

covid_data_1 = covid_data.groupby(['date'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()

covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('corona-logo-1.jpg'),
                     id='corona-image',
                     style={
                         "height": "60px",
                         "width": "auto",
                         "margin-bottom": "25px",
                     },
                     )
        ],
            className="one-third column",
        ),
        html.Div([
            html.Div([
                html.H3("Covid - 19", style={"margin-bottom": "0px", 'color': 'white'}),
                html.H5("Track Covid - 19 Cases", style={"margin-top": "0px", 'color': 'white'}),
            ])
        ], className="one-half column", id="title"),

        html.Div([
            html.H6('Last Updated: ' + str(covid_data_1['date'].iloc[-1].strftime("%B %d, %Y")) + '  00:01 (UTC)',
                    style={'color': 'orange'}),

        ], className="one-third column", id='title1'),

    ], id="header", className="row flex-display", style={"margin-bottom": "25px"}),

html.Div([
        html.Div([


            html.P('Select Country', className = 'fix_label', style = {'color': 'white', 'margin-top': '2px'}),
            dcc.Dropdown(id = 'w_countries',
                         multi = False,
                         clearable = True,
                         disabled = False,
                         style = {'display': True},
                         value = 'Russia',
                         placeholder = 'Select state',
                         options = [{'label': c, 'value': c}
                                    for c in (covid_data['Country/Region'].unique())], className = 'dcc_compon'),


            ], className = "create_container2 four columns", style = {'margin-bottom': '20px', "margin-top": "20px"}),

    ], className = "row flex-display"),

html.Div([
         html.Div([
              html.Div(id='live_text1'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),


         html.Div([
              html.Div(id='live_text2'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),

         html.Div([
              html.Div(id='live_text3'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),


         html.Div([
              html.Div(id='live_text4'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),

         html.Div([
              html.Div(id='live_text5'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),

         html.Div([
              html.Div(id='live_text6'),

         ], className = "create_container two columns", style = {'text-align': 'center'}),

    ], className = "row flex-display"),

    ], id="mainContainer",
    style={"display": "flex", "flex-direction": "column"})

@app.callback(
    Output('live_text1', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    total_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1]
    today_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-2]



    return [
               html.H6(children = 'Confirmed Cases',
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(total_confirmed),
                      style={'textAlign': 'center',
                             'color': 'orange',
                             'fontSize': 40}
                      ),
               html.P('Today:  ' + ' ' + '{0:,.0f}'.format(today_confirmed)
                      + ' (' + str(round(((today_confirmed) / total_confirmed) * 100, 2)) + '%' + ' ' + 'vs last day)',
                      style = {
                          'textAlign': 'center',
                          'color': 'orange',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text2', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    total_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-1]
    today_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-1] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-2]



    return [
               html.H6(children = 'Deaths',
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(total_death),
                      style={'textAlign': 'center',
                             'color': '#dd1e35',
                             'fontSize': 40}
                      ),
               html.P('Today:  ' + ' ' + '{0:,.0f}'.format(today_death)
                      + ' (' + str(round(((today_death) / total_death) * 100, 2)) + '%' + ' ' + 'vs last day)',
                      style = {
                          'textAlign': 'center',
                          'color': '#dd1e35',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text3', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    total_recovered = covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-1]
    today_recovered = covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-1] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-2]



    return [
               html.H6(children = 'Recovered',
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(total_recovered),
                      style={'textAlign': 'center',
                             'color': 'green',
                             'fontSize': 40}
                      ),
               html.P('Today:  ' + ' ' + '{0:,.0f}'.format(today_recovered)
                      + ' (' + str(round(((today_recovered) / total_recovered) * 100, 2)) + '%' + ' ' + 'vs last day)',
                      style = {
                          'textAlign': 'center',
                          'color': 'green',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text4', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    total_active = covid_data_2[covid_data_2['Country/Region'] == w_countries]['active'].iloc[-1]
    today_active = covid_data_2[covid_data_2['Country/Region'] == w_countries]['active'].iloc[-1] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['active'].iloc[-2]



    return [
               html.H6(children = 'Active',
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P('{0:,.0f}'.format(total_active),
                      style={'textAlign': 'center',
                             'color': '#e55467',
                             'fontSize': 40}
                      ),
               html.P('Today:  ' + ' ' + '{0:,.0f}'.format(today_active)
                      + ' (' + str(round(((today_active) / total_active) * 100, 2)) + '%' + ' ' + 'vs last day)',
                      style = {
                          'textAlign': 'center',
                          'color': '#e55467',
                          'fontSize': 15,
                          'margin-top': '-18px'}
                      )

    ]

@app.callback(
    Output('live_text5', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    total_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1]
    total_recovered = covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-1]
    today_recovered = covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-1] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['recovered'].iloc[-2]




    return [
               html.H6(children = 'Recovery Rate',
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P(str(round(((total_recovered) / total_confirmed) * 100, 2)) + '%',
                      style={'textAlign': 'center',
                             'color': '#0FECE9',
                             'fontSize': 40}
                      ),
               # html.P('Today:  ' + ' ' + str(round(((today_recovered) / total_confirmed) * 100, 2)) + '%',
               #        style = {
               #            'textAlign': 'center',
               #            'color': '#0FECE9',
               #            'fontSize': 15,
               #            'margin-top': '-18px'}
               #        )

    ]

@app.callback(
    Output('live_text6', 'children'),
    [Input('w_countries', 'value')]
    )

def update_graph(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[['confirmed', 'death', 'recovered', 'active']].sum().reset_index()
    total_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1]
    total_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-1]
    today_death = covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-1] - covid_data_2[covid_data_2['Country/Region'] == w_countries]['death'].iloc[-2]




    return [
               html.H6(children = 'Mortality Rate',
                       style={'textAlign': 'center',
                              'color': 'white'}
                       ),
               html.P(str(round(((total_death) / total_confirmed) * 100, 2)) + '%',
                      style={'textAlign': 'center',
                             'color': '#dd1e35',
                             'fontSize': 40}
                      ),
               # html.P('Today:  ' + ' ' + str(round(((today_death) / total_confirmed) * 100, 2)) + '%',
               #        style = {
               #            'textAlign': 'center',
               #            'color': '#E93CB7',
               #            'fontSize': 15,
               #            'margin-top': '-18px'}
               #        )

    ]


if __name__ == '__main__':
    app.run_server(debug=True)