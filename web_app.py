import pandas as pd
import dash
import dash_bootstrap_components as dbc
# from jupyter_dash import JupyterDash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash.exceptions import PreventUpdate

# Your Mapbox token 
px.set_mapbox_access_token('')

# Load the dataset
df = pd.read_csv('hwo_data_1223.csv')





# List of columns to ensure are numeric, excluding T1, T2, T3, and T4
numeric_columns = ['Temp', 'Salinity', 'DO', 'DO_sat', 'pH', 'Turbidity', 'TotalN', 'TotalP', 'Entero']

# Convert columns to numeric and fill NaN values with the mean value for each location
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Fill NaN values with the mean value for each location
df = df.groupby('SiteName').apply(lambda group: group.fillna(group.mean()))
df.reset_index(drop=True, inplace=True)

# Remove Beach and Park from SiteName
df['SiteName'] = df['SiteName'].str.replace('Beach','').str.replace('Park','')

# Ensure 'Date' column is in datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Year Column
df['Year'] = df['Date'].dt.year.astype('str')

# Select the most recent data point for each location
df_most_recent = df.sort_values(by='Date').groupby('SiteName').tail(1)

# Create the df with average values of each location
df_average = df.groupby('SiteName')[numeric_columns+['Lat','Long']].mean().reset_index()


# Initialize the JupyterDash app
app = dash.Dash(__name__)


# Available Plotly themes
plotly_themes = [
    'plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white', 'none'
]

# Plotly Fig height
height = 390


# ###########  Testing


# scatter_fig1 = px.scatter(
#     filtered_df, x='Temp', y='Salinity', title='Temperature vs Salinity', 
#     hover_data=['SiteName', 'Date'], color='SiteName', template=theme
# )
# scatter_fig2 = px.scatter(
#     filtered_df, x='DO', y='pH', title='Dissolved Oxygen vs pH', 
#     hover_data=['SiteName', 'Date'], color='SiteName', template=theme
# )
# scatter_fig3 = px.scatter(
#     filtered_df, x='TotalN', y='TotalP', title='Nitrogen vs Phosphorus', 
#     hover_data=['SiteName', 'Date'], color='SiteName', template=theme
# )
# scatter_fig4 = px.scatter(
#     filtered_df, x='Turbidity', y='Entero', title='Turbidity vs Enterococcus', 
#     hover_data=['SiteName', 'Date'], color='SiteName', template=theme
# )

# # Only display the legend in the first scatter plot
# scatter_fig1.update_layout(xaxis_title='Temperature (C)', yaxis_title='Salinity (ppt)', height=height)
# scatter_fig2.update_layout(xaxis_title='Dissolved Oxygen (mg/L)', yaxis_title='pH', height=height, showlegend=False)
# scatter_fig3.update_layout(xaxis_title='Nitrogen (ug/L)', yaxis_title='Phosphorus (ug/L)', height=height, showlegend=False)
# scatter_fig4.update_layout(xaxis_title='Turbidity (NTU)', yaxis_title='Enterococcus (MPN)', height=height, showlegend=False)




##############




app.layout = html.Div([
    html.Div([
        html.Img(src='logo.png', style={'width': '100px', 'height': 'auto', 'margin-right': '10px'}),
        html.H1("Hawai'i Wai Ola - Water Quality Dashboard", style={'display': 'inline-block', 'vertical-align': 'middle'})
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
    # html.P("This data is obtained by the Hawai'i Wai Ola NGO and their group of volunteers. We look for sediments, nutrients, and other pollutants from land-based sources that might be having a negative impact on water quality. Data is collected for ocean salinity, pH, temperature, organic nutrients (nitrogen and phosphorus compounds), dissolved oxygen (DO), and turbidity.",
        #    style={'text-align': 'center', 'max-width': '800px', 'margin': '0 auto'}),
    html.Div([
        html.Label('Select a theme: '),
        dcc.Dropdown(
            id='theme-selector',
            options=[{'label': theme, 'value': theme} for theme in plotly_themes],
            value='plotly_dark',
            style={'width': '200px', 'display': 'inline-block'}
        ),
    ], style={'position': 'absolute', 'top': '20px', 'right': '20px'}),
    html.Div([ dcc.Checklist(
        id='location-checklist',
        options=[
            {'label': 'Hilo', 'value': 'Hilo'},
            {'label': 'South Kohala', 'value': 'South Kohala'},
            {'label': 'Kona', 'value': 'Kona'}
        ],
        value=['Hilo', 'South Kohala', 'Kona'],  # Default selected values
        style={'display': 'inline-block', 'padding': '0px 10px'}
        )
        ], style={'margin': '0px', 'text-align': 'center', 'width': '100%'}),
    html.Div([
        html.Div([
            html.Div([
                    html.Button('Show All Locations', id='reset-button', n_clicks=0, style={'margin': '5px auto', 'display': 'inline-block', 'width': '45%', 'height': '20px', 'padding': '5px 5px'}),
                    html.Div([
                                html.Label('Color by:'),
                                dcc.Dropdown(
                                    id='color-selector',
                                    options=[
                                        {'label': 'SiteName', 'value': 'SiteName'},
                                        {'label': 'Year', 'value': 'Year'}
                                    ],
                                    value='SiteName',  # Default value
                                    style={'width': '200px', 'display': 'inline-block'}
                                )
                            ], style={'margin': '5px', 'display': 'inline-block','width': '45%'})

                      ],style={'display': 'inline-block'}),
            html.Div([
                html.Div([dcc.Graph(id='scatter-plot-1')], style={'width': '48%', 'display': 'inline-block', 'padding': '2px', 'margin': '1px'}),
                html.Div([dcc.Graph(id='scatter-plot-2')], style={'width': '48%', 'display': 'inline-block', 'padding': '2px', 'margin': '1px'}),
                html.Div([dcc.Graph(id='scatter-plot-3')], style={'width': '48%', 'display': 'inline-block', 'padding': '2px', 'margin': '1px'}),
                html.Div([dcc.Graph(id='scatter-plot-4')], style={'width': '48%', 'display': 'inline-block', 'padding': '2px', 'margin': '1px'}),
            ])
        ], style={'display': 'flex', 'flex-wrap': 'wrap', 'width': '50%', 'padding': '10px', 'margin': '0 auto'}),
        html.Div([
            html.Div([
                html.Label('Select a field for map point size and time series: '),
                dcc.Dropdown(
                    id='size-selector',
                    options=[
                        {'label': 'Temperature (C)', 'value': 'Temp'},
                        {'label': 'Salinity (ppt)', 'value': 'Salinity'},
                        {'label': 'Dissolved Oxygen (mg/L)', 'value': 'DO'},
                        {'label': 'Oxygen Saturation (%)', 'value': 'DO_sat'},
                        {'label': 'pH', 'value': 'pH'},
                        {'label': 'Turbidity (NTU)', 'value': 'Turbidity'},
                        {'label': 'Nitrogen (ug/L)', 'value': 'TotalN'},
                        {'label': 'Phosphorus (ug/L)', 'value': 'TotalP'},
                        {'label': 'Enterococcus (MPN)', 'value': 'Entero'}
                    ],
                    value='Temp',
                    style={'width': '200px', 'display': 'inline-block'}
                ),
            ], style={'margin': '10px', 'text-align': 'center'}),
            html.Div([
                html.Div([dcc.Graph(id='map-graph')],style={'padding':'2px'}),
                html.Div([dcc.Graph(id='time-series-graph')],style={'padding':'2px'})
                    ])
        ], style={'width': '50%', 'padding': '10px', 'margin': '0 auto'})
    ], style={'display': 'flex'}),
])
@app.callback(
    [Output('scatter-plot-1', 'figure'),
     Output('scatter-plot-2', 'figure'),
     Output('scatter-plot-3', 'figure'),
     Output('scatter-plot-4', 'figure')],
    [Input('map-graph', 'clickData'),
     Input('reset-button', 'n_clicks'),
     Input('theme-selector', 'value'),
     Input('location-checklist', 'value'),
     Input('color-selector','value')],
    [State('map-graph', 'clickData')]
)
def update_scatter_plots(clickData, n_clicks, theme, selected_locations, color_axis_value, map_click_data):
    ctx = dash.callback_context

    # Filter based on the selected locations
    filtered_df = df[
        ((df['Long'] > -155.1) & ('Hilo' in selected_locations)) |
        ((df['Long'] < -155.9) & ('Kona' in selected_locations)) |
        ((df['Lat'] > 19.9) & ('South Kohala' in selected_locations))
    ]

    # Check if filtered_df is empty
    if filtered_df.empty:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update


    # Determine which input triggered the callback
    if not ctx.triggered:
        pass  # filtered_df is already set by location filter
    else:
        triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

        if triggered_input == 'reset-button':
            # Reset button was clicked
            filtered_df = df
        elif triggered_input == 'map-graph' and clickData:
            # Map point was clicked
            lat = clickData['points'][0]['lat']
            lon = clickData['points'][0]['lon']
            filtered_df = filtered_df[(filtered_df['Lat'] == lat) & (filtered_df['Long'] == lon)]

    scatter_fig1 = px.scatter(
        filtered_df, x='Temp', y='Salinity', title='Temperature vs Salinity', 
        hover_data=['SiteName', 'Date'], color=color_axis_value, template=theme,
        color_discrete_sequence=px.colors.qualitative.G10
    )
    scatter_fig2 = px.scatter(
        filtered_df, x='DO', y='pH', title='Dissolved Oxygen vs pH', 
        hover_data=['SiteName', 'Date'], color=color_axis_value, template=theme,
        color_discrete_sequence=px.colors.qualitative.G10
    )
    scatter_fig3 = px.scatter(
        filtered_df, x='TotalN', y='TotalP', title='Nitrogen vs Phosphorus', 
        hover_data=['SiteName', 'Date'], color=color_axis_value, template=theme,
        color_discrete_sequence=px.colors.qualitative.G10
    )
    scatter_fig4 = px.scatter(
        filtered_df, x='Turbidity', y='Entero', title='Turbidity vs Enterococcus', 
        hover_data=['SiteName', 'Date'], color=color_axis_value, template=theme,
        color_discrete_sequence=px.colors.qualitative.G10
    )

    # Only display the legend in the first scatter plot
    scatter_fig1.update_layout(xaxis_title='Temperature (C)', yaxis_title='Salinity (ppt)', height=height)
    scatter_fig2.update_layout(xaxis_title='Dissolved Oxygen (mg/L)', yaxis_title='pH', height=height, showlegend=True)
    scatter_fig3.update_layout(xaxis_title='Nitrogen (ug/L)', yaxis_title='Phosphorus (ug/L)', height=height, showlegend=True)
    scatter_fig4.update_layout(xaxis_title='Turbidity (NTU)', yaxis_title='Enterococcus (MPN)', height=height, showlegend=True)

    return scatter_fig1, scatter_fig2, scatter_fig3, scatter_fig4


@app.callback(
    [Output('map-graph', 'figure'),
     Output('time-series-graph', 'figure')],
    [Input('size-selector', 'value'),
     Input('theme-selector', 'value'),
     Input('location-checklist', 'value')]
)
def update_map_and_time_series(selected_size, theme, selected_locations):
    # Filter based on the selected locations
    filtered_df = df_average[
        ((df_average['Long'] > -155.1) if 'Hilo' in selected_locations else False) |
        ((df_average['Long'] < -155.9) if 'Kona' in selected_locations else False) |
        ((df_average['Lat'] > 19.9)  if 'South Kohala' in selected_locations else False)
    ]

    # Check if filtered_df is empty
    if filtered_df.empty:
        return dash.no_update, dash.no_update

    map_fig = px.scatter_mapbox(
        filtered_df, 
        lat="Lat", 
        lon="Long", 
        color_discrete_sequence=["cyan"],
        size=selected_size,
        hover_name="SiteName",
        hover_data=["Temp", "Salinity", "DO", "pH", "Turbidity", "TotalN", "TotalP", "Entero"],
        # title="Water Quality Metrics Map",
        mapbox_style="satellite",  # Updated map theme to satellite
        zoom=7,  # Adjusted zoom level for better view
        template=theme
    )
    map_fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1}, height=height)
    time_series_fig = px.line(
        df[df['SiteName'].isin(filtered_df['SiteName'])], 
        x='Date', 
        y=selected_size, 
        color='SiteName',
        title=f"Time Series of {selected_size}",
        labels={"SiteName": "SiteName", "Date": "Date"},
        template=theme
    )

    time_series_fig.update_layout(
        xaxis=dict(#rangeslider=dict(visible=True), 
                fixedrange=False, title=f"Date"),
        yaxis=dict(fixedrange=False),
        yaxis_title=f"{[label for label, value in zip(['Temperature (C)', 'Salinity (ppt)', 'Dissolved Oxygen (mg/L)', 'Oxygen Saturation (%)', 'pH', 'Turbidity (NTU)', 'Nitrogen (ug/L)', 'Phosphorus (ug/L)', 'Enterococcus (MPN)'], numeric_columns) if value == selected_size][0]}",
        legend_title="SiteName",
        height=height,  # Updated height variable
        margin={"r":170,"t":65,"l":0,"b":60}
    )

    return map_fig, time_series_fig

if __name__ == '__main__':
    app.run_server(debug=False)





