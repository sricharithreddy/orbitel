import streamlit as st
import pandas as pd
from utils.data_loader import load_and_clean_data
from utils.analysis import (
    call_level_funnel, 
    initial_lead_funnel, 
    lost_lead_breakdown, 
    deep_dive_profiles, 
    time_based_impact, 
    duration_analysis, 
    gender_analysis, 
    final_lead_funnel
)
from utils.export_utils import download_buttons, table_to_png_download

st.set_page_config(page_title="Lead Analysis Dashboard", layout="wide")

st.title("📊 Lead Analysis Dashboard")

# File uploader
uploaded_files = st.file_uploader(
    "Upload call campaign Excel/CSV files", 
    type=["xlsx","csv"], 
    accept_multiple_files=True
)

if uploaded_files:
    df = load_and_clean_data(uploaded_files)

    if df.empty:
        st.warning("No data after cleaning. Please check the file.")
    else:
        # Date filter
        min_date, max_date = df['date'].min(), df['date'].max()
        date_range = st.date_input(
            "Select Date Range", 
            [min_date, max_date], 
            min_value=min_date, 
            max_value=max_date
        )
        df = df[(df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))]

        if df.empty:
            st.warning("No data in this date range.")
        else:
            # KPI row
            st.subheader("📌 Overview KPIs")
            kpis = {
                "Total Dials": len(df),
                "Unique Leads": df['mobile_number'].nunique(),
                "Conversion Count": (df['outcome_norm']=="converted").sum(),
                "Contact Rate %": round((~df['outcome_norm'].isin(["busy","no_answer","failed","unknown"])).mean()*100,2)
            }
            st.metric("Total Dials", kpis["Total Dials"])
            st.metric("Unique Leads", kpis["Unique Leads"])
            st.metric("Conversions", kpis["Conversion Count"])
            st.metric("Contact Rate", f"{kpis['Contact Rate %']}%")

            # Tabs = slides
            tabs = st.tabs([
                "Slide 1: Dual Funnel",
                "Slide 2: Lost Breakdown",
                "Slide 3: Not Interested",
                "Slide 4: Other Lost",
                "Slide 5: Advanced Insights",
                "Slide 6: Final Funnel",
                "Slide 7: Recommendations"
            ])

            with tabs[0]:
                st.subheader("Call-Level Funnel")
                call_table = call_level_funnel(df)
                st.dataframe(call_table, use_container_width=True)
                download_buttons(call_table, "call_level_funnel")
                table_to_png_download(call_table, "call_level_funnel")

                st.subheader("Initial Lead-Level Funnel")
                init_table = initial_lead_funnel(df)
                st.dataframe(init_table, use_container_width=True)
                download_buttons(init_table, "initial_lead_funnel")
                table_to_png_download(init_table, "initial_lead_funnel")

            with tabs[1]:
                st.subheader("Lost Leads Breakdown")
                lost_table = lost_lead_breakdown(df)
                st.dataframe(lost_table, use_container_width=True)
                download_buttons(lost_table, "lost_lead_breakdown")
                table_to_png_download(lost_table, "lost_lead_breakdown")

            with tabs[2]:
                st.subheader("Deep Dive: Not Interested")
                prof = deep_dive_profiles(df, reason="Not Interested")
                st.dataframe(prof, use_container_width=True)
                download_buttons(prof, "deep_dive_not_interested")
                table_to_png_download(prof, "deep_dive_not_interested")

            with tabs[3]:
                st.subheader("Deep Dive: Other Lost Reasons")
                prof = deep_dive_profiles(df, reason="Other")
                st.dataframe(prof, use_container_width=True)
                download_buttons(prof, "deep_dive_other")
                table_to_png_download(prof, "deep_dive_other")

            with tabs[4]:
                st.subheader("Time-Based Impact (Day of Week)")
                dow, hour = time_based_impact(df)
                st.dataframe(dow, use_container_width=True)
                st.dataframe(hour, use_container_width=True)
                download_buttons(dow, "dow_impact")
                download_buttons(hour, "hour_impact")

                st.subheader("Call Duration")
                dur = duration_analysis(df)
                st.dataframe(dur, use_container_width=True)
                download_buttons(dur, "duration_analysis")

                st.subheader("Gender Impact")
                gen = gender_analysis(df)
                st.dataframe(gen, use_container_width=True)
                download_buttons(gen, "gender_analysis")

            with tabs[5]:
                st.subheader("Final Lead Funnel (User Logic)")
                final_table = final_lead_funnel(df)
                st.dataframe(final_table, use_container_width=True)
                download_buttons(final_table, "final_lead_funnel")
                table_to_png_download(final_table, "final_lead_funnel")

            with tabs[6]:
                st.subheader("Strategic Recommendations")
                st.markdown("""
                1. Reduce "No Answer" & "Uncontacted" through smart retries in best-performing hours.  
                2. Introduce objection-handling scripts for "Not Interested" leads.  
                3. Enforce SLA for "Agent Assigned" to ensure fast conversions.  
                4. Train agents to aim for 90+ sec conversations for higher conversions.  
                5. Improve data hygiene to filter out wrong numbers.
                """)
else:
    st.info("👆 Please upload at least one Excel/CSV file to begin.")
