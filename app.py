import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tesla EV Dashboard", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #111111;
            color: #e0e0e0;
        }
        .css-18e3th9 {
            background-color: #111111;
        }
        .stApp {
            background-color: #111111;
        }
        .css-1d391kg, .css-1cpxqw2, .css-1v0mbdj {
            color: #e0e0e0;
        }
        h1, h2, h3, h4 {
            color: #72d1ff;
        }
        hr {
            border-top: 1px solid #72d1ff;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🔍 Navigation")
import streamlit_option_menu

with st.sidebar:
    st.markdown("### ⚡ Project Sections")

    page = streamlit_option_menu.option_menu(
        "Navigation",
        ["📊 Power BI Dashboard", "📈 Streamlit Visuals", "📘 EDA Summary", "❓ Key Insights"],
        icons=["bar-chart", "graph-up", "book", "question-circle"],
        menu_icon="menu-button-wide",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#0e1117"},
            "icon": {"color": "#72d1ff", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "color":"#c2c2c2"},
            "nav-link-selected": {"background-color": "#72d1ff", "color": "black"},
        }
    )

sales_df = pd.read_csv("clean_ev_sales.csv")
station_df = pd.read_csv("clean_station_usage.csv")
regional_df = pd.read_csv("clean_regional_factors_1.csv")

def clean_sales(df):
    df = df[df['parameter'] == 'EV Sales']
    df = df[df['value'].notna()]
    return df

sales_df = clean_sales(sales_df)
station_df['AvgWaitTime'] = station_df['AvgWaitTime'].str.extract(r'(\d+)').astype(float)

if page == "📊 Power BI Dashboard":
    st.title("Tesla EV Demand vs Charging Supply Dashboard")
    st.markdown("Explore real-time analytics of Tesla EV trends and charging station load.")

    st.markdown(
        """
        <iframe title="dsbi dashboard" width="1140" height="541.25"
        src="https://app.powerbi.com/reportEmbed?reportId=7fa44beb-d571-42e8-b736-87224273297e&autoAuth=true&ctid=23035d1f-133c-44b5-b2ad-b3aef17baaa1"
        frameborder="0" allowFullScreen="true"></iframe>
        """,
        unsafe_allow_html=True
    )

elif page == "📈 Streamlit Visuals":
    st.title("Interactive Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        selected_region = st.selectbox("Select Region", sorted(sales_df['region'].unique()))
    with col2:
        selected_year = st.selectbox("Select Year", sorted(sales_df['year'].unique()))

    st.subheader("🔹 Key Metrics")
    kpi1, kpi2, kpi3 = st.columns(3)
    region_sales = sales_df[(sales_df['region'] == selected_region) & (sales_df['year'] == selected_year)]['value'].sum()
    wait_time = station_df[station_df['region'] == selected_region]['AvgWaitTime'].mean()
    sessions = station_df[station_df['region'] == selected_region]['TotalSessions'].sum()
    kpi1.metric("Total EV Sales", f"{int(region_sales):,}")
    kpi2.metric("Avg Wait Time (min)", f"{wait_time:.1f}")
    kpi3.metric("Charging Sessions", f"{int(sessions):,}")

    st.subheader("📊 EV Sales Over Time")
    trend_data = sales_df[sales_df['region'] == selected_region]
    fig1 = px.line(trend_data, x='year', y='value', color='mode', markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("⚡ Station Load by Location")
    station_region = station_df[station_df['region'] == selected_region]
    fig2 = px.bar(station_region, x='StationID', y='TotalSessions', color='AvgWaitTime', color_continuous_scale='teal')
    st.plotly_chart(fig2, use_container_width=True)

elif page == "📘 EDA Summary":
    st.title("EDA Notebook Preview")
    with open("eda_output.html", "r", encoding="utf-8") as f:
        eda_html = f.read()
    st.components.v1.html(eda_html, height=800, scrolling=True)

elif page == "❓ Key Insights":
    st.title("Data Exploration Analysis Questions")

    st.markdown("### 📍 Which regions have high EV sales but fewer stations?")
    merged_df = pd.merge(sales_df.groupby('region')['value'].sum().reset_index(),
                         regional_df[['region', 'ExistingStations']], on='region')
    merged_df.rename(columns={'value': 'EV_Sales'}, inplace=True)
    fig = px.scatter(merged_df, x='ExistingStations', y='EV_Sales', text='region',
                     color='EV_Sales', size='EV_Sales', labels={'EV_Sales': 'EV Sales'},
                     title='EV Sales vs Existing Charging Stations')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### ⚠️ Are there stations with long wait times but low sessions?")
    station_check = station_df[['StationID', 'TotalSessions', 'AvgWaitTime']]
    fig = px.scatter(station_check, x='TotalSessions', y='AvgWaitTime', color='AvgWaitTime',
                     hover_data=['StationID'], title='Sessions vs Wait Time')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📈 What modes (cars, buses, bikes) are trending across regions?")
    mode_trend = sales_df.groupby(['region', 'mode'])['value'].sum().reset_index()
    fig = px.bar(mode_trend, x='region', y='value', color='mode', barmode='group',
                 title='EV Sales by Mode per Region')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧭 How does average wait time relate to EV adoption rate?")
    combined = pd.merge(station_df.groupby('region')['AvgWaitTime'].mean().reset_index(),
                        regional_df[['region', 'EV_AdoptionRate']], on='region')
    fig = px.scatter(combined, x='EV_AdoptionRate', y='AvgWaitTime',
                     trendline='ols', color='AvgWaitTime',
                     title='EV Adoption Rate vs Avg Wait Time')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 💡 Which years saw the most EV growth by region?")
    growth = sales_df.groupby(['region', 'year'])['value'].sum().reset_index()
    fig = px.line(growth, x='year', y='value', color='region', markers=True,
                  title='Yearly EV Sales Growth by Region')
    st.plotly_chart(fig, use_container_width=True)
