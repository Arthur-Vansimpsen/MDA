import faicons as fa
import pandas as pd
import joblib
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget
from htmltools import HTML
import pathlib
import plotly.graph_objects as go
import plotly.io as pio
from shiny import render

# Load model
model_path = pathlib.Path(__file__).parent / "1stmodel1"
model = joblib.load(model_path)
# Load Sankey dataset
df_sankey = pd.read_csv(pathlib.Path(__file__).parent / "oscar_SciProject.csv")
df_sankey.loc[:, 'ecMaxContribution'] = df_sankey['Scifunding']
country_list = ["All", "AT", "BE", "DE", "EL", "ES", "FI", "FR", "IT", "NL", "NO","SE", "UK"]

ICONS = {
    "user": fa.icon_svg("money-bill-transfer", style = "solid", ),
    "wallet": fa.icon_svg("money-bill", style = "solid", stroke="red"),
    "currency-dollar": fa.icon_svg("money-bill", "solid", fill="green"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

# UI
app_ui = ui.page_sidebar(
    ui.sidebar(
            ui.h2("🎯 Contribution Prediction Tool"),
        ui.h4("🔧 Project Parameters"),
        ui.row(
            ui.column(6, ui.input_numeric("duration", "Project Duration (days)", value=0, min=0, max=3700)),
            ui.column(6, ui.input_select("month", "Start Month", {
                str(i): name for i, name in enumerate(
                    ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"], 1)
            })),
            ui.column(6, ui.input_numeric("contributers", "Contributors", value=1, min=1, max=10)),
            ui.column(6, ui.input_select("country1", "Coordinator Country", {
                "ES": "Spain", "PL": "Poland", "DE": "Germany", "FR": "France", "FI": "Finland", "IL": "Israel",
                "NL": "Netherlands", "NO": "Norway", "IT": "Italy", "SE": "Sweden", "PT": "Portugal", "TR": "Turkey",
                "CZ": "Czech Rep.", "AT": "Austria", "DK": "Denmark", "BE": "Belgium", "IE": "Ireland", "EL": "Greece",
                "IS": "Iceland", "LU": "Luxembourg", "SI": "Slovenia", "CH": "Switzerland", "RO": "Romania", "HU": "Hungary",
                "EE": "Estonia", "CY": "Cyprus", "UK": "UK", "AL": "Albania", "RS": "Serbia", "ME": "Montenegro",
                "SK": "Slovakia", "LT": "Lithuania", "BA": "Bosnia", "FO": "Faroe Islands", "MD": "Moldova", "MT": "Malta",
                "BG": "Bulgaria", "HR": "Croatia", "LV": "Latvia", "UA": "Ukraine", "TN": "Tunisia", "GE": "Georgia",
                "ZA": "South Africa", "AM": "Armenia", "KE": "Kenya", "GH": "Ghana", "NG": "Nigeria", "MK": "North Macedonia",
                "AU": "Australia"
            })),
            ui.column(6, ui.input_select("project_type", "Participant Type", {
                "REC": "Research Org", "HEC": "Education", "OTH": "Other", "PRC": "Private", "PUB": "Public"
            })),
            ui.column(6, ui.input_select("funding_scheme", "Funding Scheme", {
                "HORIZON-ERC": "HORIZON-ERC", "HORIZON-AG": "HORIZON-AG", "ERC": "ERC", "HORIZON-CSA": "HORIZON-CSA",
                "HORIZON-RIA": "HORIZON-RIA", "HORIZON-EIC": "HORIZON-EIC", "EURATOM-COFUND": "EURATOM-COFUND",
                "MSCA-PF": "MSCA-PF", "CSA": "CSA", "HORIZON-COFUND": "HORIZON-COFUND",
                "HORIZON-TMA-MSCA-PF-EF": "HORIZON-TMA-MSCA-PF-EF", "HORIZON-AG-LS": "HORIZON-AG-LS",
                "HORIZON-AG-UN": "HORIZON-AG-UN", "HORIZON-IA": "HORIZON-IA", "HORIZON-ERC-POC": "HORIZON-ERC-POC",
                "EIC": "EIC", "HORIZON-TMA-MSCA-PF-GF": "HORIZON-TMA-MSCA-PF-GF", "EURATOM-CSA": "EURATOM-CSA",
                "EURATOM-RIA": "EURATOM-RIA", "ERC-POC": "ERC-POC", "EURATOM-IA": "EURATOM-IA",
                "HORIZON-TMA-MSCA-DN-ID": "HORIZON-TMA-MSCA-DN-ID", "HORIZON-TMA-MSCA-DN": "HORIZON-TMA-MSCA-DN",
                "HORIZON-ERC-SYG": "HORIZON-ERC-SYG", "ERC-SYG": "ERC-SYG", "HORIZON-TMA-MSCA-DN-JD": "HORIZON-TMA-MSCA-DN-JD",
                "RIA": "RIA", "HORIZON-TMA-MSCA-SE": "HORIZON-TMA-MSCA-SE", "HORIZON-TMA-MSCA-Cofund-P": "Cofund-P",
                "HORIZON-TMA-MSCA-Cofund-D": "Cofund-D", "IA": "IA", "HORIZON-PCP": "HORIZON-PCP",
                "HORIZON-JU-RIA": "HORIZON-JU-RIA", "HORIZON-JU-IA": "HORIZON-JU-IA", "HORIZON-JU-CSA": "HORIZON-JU-CSA",
                "HORIZON-EIT-KIC": "HORIZON-EIT-KIC", "HORIZON-EIC-ACC-BF": "HORIZON-EIC-ACC-BF",
                "HORIZON-EIC-ACC": "HORIZON-EIC-ACC", "EIC-ACC": "EIC-ACC"
            }))),
        ui.h4("📚 Scientific Domains (Binary 0 or 1)"),
        ui.row(
            ui.column(6, ui.input_numeric("agricultural_sciences", "Agricultural Sciences", value=0, min=0, max=1)),
            ui.column(6, ui.input_numeric("engineering_and_technology", "Engineering & Technology", value=0, min=0, max=1)),
            ui.column(6, ui.input_numeric("humanities", "Humanities", value=0, min=0, max=1)),
            ui.column(6, ui.input_numeric("medical_and_health_sciences", "Medical & Health Sciences", value=0, min=0, max=1)),
            ui.column(6, ui.input_numeric("natural_sciences", "Natural Sciences", value=0, min=0, max=1)),
            ui.column(6, ui.input_numeric("social_sciences", "Social Sciences", value=0, min=0, max=1)),
        ui.input_action_button("predict", "🔍 Predict", class_="btn-primary")),
        ui.h2("🔀 Sankey Diagram"),
        ui.input_select("country", "Select Country:", choices=country_list, selected="All"),
        width="550px",
        open="desktop",
    ),
    ui.layout_columns(
        ui.value_box("Predicted class", ui.output_ui("predicted_class"), showcase=ICONS["user"]),
        ui.value_box("Minimum for this class", ui.output_ui("average_tip"), showcase=ICONS["wallet"]),
        ui.value_box("Maximum for this class", ui.output_ui("average_bill"), showcase=ICONS["currency-dollar"]),
        fill=False,
    ),
    ui.layout_columns(
        ui.card(ui.card_header("Predicted probabilities"), ui.output_ui("prediction_table"), full_screen=True),
        ui.card(ui.card_header("Shapley values"), ui.output_image("image"), full_screen=True),
        ui.card(ui.card_header("Sankey diagram per country"), output_widget("sankey"), full_screen=True),
        col_widths=[6, 6, 12],
    ),
    title="Project proposal prediction tool",
    fillable=True,
)

# Server
def server(input, output, session):
    @reactive.calc
    def model_input():
        return pd.DataFrame({
            "duration": [input.duration()],
            "month": [input.month()],
            "agricultural sciences": [input.agricultural_sciences()],
            "engineering and technology": [input.engineering_and_technology()],
            "humanities": [input.humanities()],
            "natural sciences": [input.natural_sciences()],
            "social sciences": [input.social_sciences()],
            "country": [input.country1()],
            "fundingScheme": [input.funding_scheme()],
            "activityType": [input.project_type()],
            "medical and health sciences": [input.medical_and_health_sciences()],
            "contributors": [input.contributers()]
        })

    @render.ui
    def predicted_class():
        if input.predict() == 0:
            return "—"
        return f"{model.predict(model_input())[0]}"
    
    @reactive.calc
    def predicted_class_value():
        if input.predict() == 0:
            return None
        return int(model.predict(model_input())[0])
        

    @render.ui
    def average_tip():
        pc = predicted_class_value()
        if pc is None:
            return "—"
        tips = {
            0: "75,000",
            1: "166,000",
            2: "191,000",
            3: "253,000",
            4: "1,494,000",
            5: "1,808,000",
            6: "2,340,000",
            7: "2,631,000",
            8: "3,991,000",
            9: "6,096,000",
        }
        return tips.get(pc, "5%")

    @render.ui
    def average_bill():
        pc = predicted_class_value()
        if pc is None:
            return "—"
        tips = {
            0: "166,000",
            1: "191,000",
            2: "253,000",
            3: "1,494,000",
            4: "1,808,000",
            5: "2,340,000",
            6: "2,631,000",
            7: "3,991,000",
            8: "6,096,000",
            9: "18,000,000",
        }
        return tips.get(pc, "5%")

    @render.ui
    def prediction_table():
        if input.predict() == 0:
            return HTML("<p>Click <b>Predict</b> to see the result.</p>")

        probs = model.predict_proba(model_input())[0]
        table_rows = "".join(f"<tr><td>Class {i}</td><td>{p:.1%}</td></tr>" for i, p in enumerate(probs))
        return HTML(f"""
            <table class="table table-bordered">
                <thead><tr><th>Class</th><th>Probability</th></tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        """)

    @output
    @render_widget
    def sankey():
        selected_country = input.country()
        data = df_sankey if selected_country == "All" else df_sankey[df_sankey["country"] == selected_country]

        if selected_country == "All":
            total_money = data['ecMaxContribution'].sum()
            country_money = (data.groupby('country')['ecMaxContribution'].sum() / total_money) * 100
            country_field_money = (data.groupby(['country', 'field'])['ecMaxContribution'].sum() / total_money) * 100
            field_activity_money = (data.groupby(['field', 'activityType'])['ecMaxContribution'].sum() / total_money) * 100

            filtered_country_money = country_money[country_money > 3]
            filtered_countries = filtered_country_money.index

            country_field_money_df = country_field_money.reset_index()
            country_field_money_df.columns = ['Country', 'Field', 'Money']
            country_field_money_df['Country'] = country_field_money_df['Country'].apply(
                lambda x: x if x in filtered_countries else 'Other')
            country_field_money_df = country_field_money_df.groupby(['Country', 'Field'], as_index=False).sum()

            field_activity_money_df = field_activity_money.reset_index()
            field_activity_money_df.columns = ['Field', 'ActivityType', 'Money']

            labels = ['SciFunding'] + country_field_money_df['Country'].unique().tolist() + country_field_money_df['Field'].unique().tolist() + field_activity_money_df['ActivityType'].unique().tolist()
        else:
            total_money = data["ecMaxContribution"].sum()
            city_money = data.groupby("city")["ecMaxContribution"].sum() / total_money * 100
            city_field_money = (data.groupby(["city", "field"])["ecMaxContribution"].sum() / total_money) * 100
            field_activity_money = (data.groupby(["field", "activityType"])["ecMaxContribution"].sum() / total_money) * 100

            filtered_city_money = city_money[city_money > 3]
            filtered_cities = filtered_city_money.index

            city_field_money_df = city_field_money.reset_index()
            city_field_money_df.columns = ['City', 'Field', 'Money']
            city_field_money_df['City'] = city_field_money_df['City'].apply(
                lambda x: x if x in filtered_cities else 'Other')
            city_field_money_df = city_field_money_df.groupby(['City', 'Field'], as_index=False).sum()

            field_activity_money_df = field_activity_money.reset_index()
            field_activity_money_df.columns = ['Field', 'ActivityType', 'Money']

            labels = ['SciFunding'] + city_field_money_df['City'].unique().tolist() + city_field_money_df['Field'].unique().tolist() + field_activity_money_df['ActivityType'].unique().tolist()

        label_to_index = {label: i for i, label in enumerate(labels)}

        if selected_country == "All":
            links1 = pd.DataFrame({
                'source': ['SciFunding'] * country_field_money_df['Country'].nunique(),
                'target': country_field_money_df['Country'].unique(),
                'value': country_field_money_df.groupby('Country')['Money'].sum().values
            })
            links2 = pd.DataFrame({
                'source': country_field_money_df['Country'],
                'target': country_field_money_df['Field'],
                'value': country_field_money_df['Money']
            })
        else:
            links1 = pd.DataFrame({
                'source': ['SciFunding'] * city_field_money_df['City'].nunique(),
                'target': city_field_money_df['City'].unique(),
                'value': city_field_money_df.groupby('City')['Money'].sum().values
            })
            links2 = pd.DataFrame({
                'source': city_field_money_df['City'],
                'target': city_field_money_df['Field'],
                'value': city_field_money_df['Money']
            })

        links3 = pd.DataFrame({
            'source': field_activity_money_df['Field'],
            'target': field_activity_money_df['ActivityType'],
            'value': field_activity_money_df['Money']
        })

        for df_link in [links1, links2, links3]:
            df_link['source'] = df_link['source'].map(label_to_index)
            df_link['target'] = df_link['target'].map(label_to_index)

        links = pd.concat([links1, links2, links3], ignore_index=True)

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue"
            ),
            link=dict(
                source=links['source'],
                target=links['target'],
                value=links['value']
            )
        )])

        fig.update_layout(title_text=f"Sankey Diagram for {selected_country}", font_size=10)
        return fig

    @render.image
    def image():
        dir = pathlib.Path(__file__).resolve().parent
        img = {"src": "www/Shapley.png", "width": "500px"}
        return img

app = App(app_ui, server)
