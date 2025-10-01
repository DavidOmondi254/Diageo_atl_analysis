import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
from query import *

st.set_page_config(page_title="Diageo ATL Marketing Analysis", layout="wide")
st.subheader("Diageo ATL Marketing Analysis") 
st.markdown("##")

# ---- SAFE NUMERIZE FUNCTION ----
def safe_numerize(value):
    try:
        if pd.isna(value):
            return "0"
        return numerize(float(value))
    except Exception:
        return str(value)  # fallback

# ---- GET DATA SAFELY ----
try:
    results, colnames = view_all_data()
    df = pd.DataFrame(results, columns=colnames) if results else pd.DataFrame()
except Exception as e:
    st.error(f"⚠️ Error loading data: {e}")
    df = pd.DataFrame()  # empty dataframe fallback

# ---- IF NO DATA ----
if df.empty:
    st.warning("⚠️ No data available to display right now.")
else:
    # Display dataframe
    st.dataframe(df)

    # Sidebar
    st.sidebar.image("data/logo1.jpg", caption="Diageo ATL Analytics", width=150)
    st.sidebar.header("Please Filter")

    Station_Type = st.sidebar.multiselect(
        "Select Station Type:", options=df["Station_Type"].unique(),
        default=df["Station_Type"].unique() if not df.empty else []
    )
    Station_Name = st.sidebar.multiselect(
        "Select Station Name:", options=df["Station_Name"].unique(),
        default=df["Station_Name"].unique() if not df.empty else []
    )
    Superbrand = st.sidebar.multiselect(
        "Select Superbrand:", options=df["Superbrand"].unique(),
        default=df["Superbrand"].unique() if not df.empty else []
    )
    Ad_Name = st.sidebar.multiselect(
        "Select Ad Name:", options=df["Ad_Name"].unique(),
        default=df["Ad_Name"].unique() if not df.empty else []
    )

    # Filter safely
    if not df.empty:
        df_selection = df.query(
            "Station_Type == @Station_Type & Station_Name == @Station_Name & Superbrand == @Superbrand & Ad_Name == @Ad_Name"
        )
    else:
        df_selection = pd.DataFrame()

    #  Add download button
    def convert_df_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode('utf-8')

    if not df_selection.empty:
        csv = convert_df_to_csv(df_selection)
        st.download_button(
            label="Download Filtered Data (CSV)",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv"
        )

    # ---- HOME SECTION ----
    def Home():
        if df_selection.empty:
            st.warning("⚠️ No records found with current filters.")
            return

        with st.expander("Tabular Data"):
            showData = st.multiselect('Choose Columns:', df_selection.columns, default=[])
            if showData:
                st.write(df_selection[showData])
            else:
                st.write(df_selection)

        # ---- KPIs ----
        if "Rate" in df_selection.columns:
            df_selection["Rate"] = pd.to_numeric(df_selection["Rate"], errors="coerce")

            total_spend = df_selection["Rate"].sum()
            total_ads = df_selection.shape[0]
            unique_brands = df_selection["Brand"].nunique()
            unique_companies = df_selection["Company_Name"].nunique()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info("Total Spend")
                st.metric(label="Total Spend", value=f"Ksh {safe_numerize(total_spend)}")
            with col2:
                st.info("Total Ads")
                st.metric(label="Total Ads", value=f"{total_ads:,}")
            with col3:
                st.info("Brands")
                st.metric(label=" Brands", value=f"{unique_brands:,}")
            with col4:
                st.info("Companies")
                st.metric(label="Companies", value=f"{unique_companies:,}")
            
            st.markdown("---")

    #  Call Home so it actually runs
    Home()

    # ---- ENSURE NUMERIC RATE ----
    if "Rate" in df_selection.columns:
        df_selection["Rate"] = pd.to_numeric(df_selection["Rate"], errors="coerce").fillna(0)

    # ---- GRAPHS ----
    st.subheader("Brand Spend Breakdown")
    fig1 = px.bar(
        df_selection,
        x="Brand",
        y="Rate",
        color="Category",
        barmode="stack",
        title="Brand Spend Breakdown"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Frequency Distribution by Week & Month")
    ads_per_week = df_selection.groupby(
        ["Year", "Week_Number", "Month"]
    )["Ad_Name"].count().reset_index(name="Ad_Count")

    fig2 = px.line(
        ads_per_week,
        x="Week_Number",
        y="Ad_Count",
        color="Month",
        markers=True,
        title="Ads per Week (expandable by Month)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader(" Share of Voice by Brand")
    sov_brand = df_selection.groupby("Brand")["Rate"].sum().reset_index()
    sov_brand["SOV %"] = (sov_brand["Rate"] / sov_brand["Rate"].sum()) * 100
    sov_brand = sov_brand.sort_values("SOV %", ascending=False)

    fig3 = px.pie(
        sov_brand,
        names="Brand",
        values="SOV %",
        title="Share of Voice - Brands"
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.write("### 🏆 Top 5 Brands by Share of Voice")
    st.table(sov_brand.head(5))

    st.subheader("Share of Voice by Company")
    sov_company = df_selection.groupby("Company_Name")["Rate"].sum().reset_index()
    sov_company["SOV %"] = (sov_company["Rate"] / sov_company["Rate"].sum()) * 100
    sov_company = sov_company.sort_values("SOV %", ascending=False)

    fig4 = px.bar(
        sov_company,
        x="Company_Name",
        y="SOV %",
        title="Share of Voice - Companies",
        text="SOV %"
    )
    fig4.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    st.plotly_chart(fig4, use_container_width=True)
    st.write("### 🏆 Top 5 Companies by Share of Voice")
    st.table(sov_company.head(5))
