import pandas as pd
import plotly.graph_objects as go
from shiny import App, render, ui, reactive
import plotly.io as pio
from htmltools import HTML

# Load dataset
df = pd.read_csv("https://raw.githubusercontent.com/Arthur-Vansimpsen/MDA/refs/heads/main/oscar_SciProject.csv")

# List of countries to choose from
country_list = ["ES", "FR", "EL", "IT", "DE", "BE", "NL", "SE", "UK"]

# UI
app_ui = ui.page_fluid(
    ui.h2("Sankey Diagram"),
    ui.input_select("country", "Select Country:", choices=country_list, selected="BE"),
    ui.output_ui("sankey_plot")
)

# Server
def server(input, output, session):

    @reactive.calc
    def filtered_data():
        return df[df["country"] == input.country()]

    @output
    @render.ui
    def sankey_plot():
        data = filtered_data()

        # Get money percentages per city, field and activity type
        total_money = data["ecMaxContribution"].sum()
        city_money = data.groupby("city")["ecMaxContribution"].sum() / total_money * 100
        city_field_money = (data.groupby(["city", "field"])["ecMaxContribution"].sum() / total_money) * 100
        field_activity_money = (data.groupby(["field", "activityType"])["ecMaxContribution"].sum() / total_money) * 100
        
        # Convert the city series to a dataframe
        city_money_df = city_money.reset_index()
        city_money_df.columns = ['City', 'Money']

        # Filter for cities with more than 3% of total money
        filtered_city_money = city_money[city_money > 3]  
        filtered_cities = filtered_city_money.index

        # Convert the city-field series to a dataframe
        city_field_money_df = city_field_money.reset_index()
        city_field_money_df.columns = ['City', 'Field', 'Money']

        # Classify cities not in the filtered list as 'Other'
        city_field_money_df['City'] = city_field_money_df['City'].apply(
            lambda x: x if x in filtered_cities else 'Other')

        # Regroup after merging to 'Other'
        city_field_money_df = city_field_money_df.groupby(['City', 'Field'], as_index=False).sum()

        # Convert the field-activity series to a dataframe
        field_activity_money_df = field_activity_money.reset_index()
        field_activity_money_df.columns = ['Field', 'ActivityType', 'Money']

        # Create a list of unique labels
        labels = ['ecMaxContribution'] + city_field_money_df['City'].unique().tolist() + city_field_money_df['Field'].unique().tolist() + field_activity_money_df['ActivityType'].unique().tolist()
        label_to_index = {label: idx for idx, label in enumerate(labels)}

        # Create two new DataFrames with the specified structure
        # 1: ecMaxContribution ➝ City
        links1 = pd.DataFrame({
            'source': ['ecMaxContribution'] * city_field_money_df['City'].nunique(),
            'target': city_field_money_df['City'].unique(),
            'value': city_field_money_df.groupby('City')['Money'].sum().values
        })

        # 2: City ➝ Field
        links2 = pd.DataFrame({
            'source': city_field_money_df['City'],
            'target': city_field_money_df['Field'],
            'value': city_field_money_df['Money']
        })

        # 3: Field ➝ ActivityType
        links3 = pd.DataFrame({
            'source': field_activity_money_df['Field'],
            'target': field_activity_money_df['ActivityType'],
            'value': field_activity_money_df['Money']
        })

        # Map source and target columns to indices in the labels list
        links1['source'] = links1['source'].map(label_to_index)
        links1['target'] = links1['target'].map(label_to_index)

        links2['source'] = links2['source'].map(label_to_index)
        links2['target'] = links2['target'].map(label_to_index)

        links3['source'] = links3['source'].map(label_to_index)
        links3['target'] = links3['target'].map(label_to_index)

        # Combine all the links
        links = pd.concat([links1, links2, links3], ignore_index=True)

        # Sankey chart
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue"
            ),
            link=dict(
                source=links["source"],
                target=links["target"],
                value=links["value"]
            )
        )])

        fig.update_layout(title_text=f"Sankey Diagram for {input.country()}", font_size=10)

        # Return Plotly figure as HTML
        return HTML(pio.to_html(fig, include_plotlyjs='cdn', full_html=False))

# Run the app
app = App(app_ui, server)
