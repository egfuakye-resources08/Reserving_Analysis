import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load Data
@st.cache_data
def load_data():
    df = pd.read_excel("kpi_summary.xlsx")
    return df

data = load_data()

# Title
st.title("Interactive Reserving Standards Dashboard")

# KPI Summary
st.subheader("Key Performance Indicators")
reserve_timely_avg = data['Reserve_Timely'].mean()
mapping_accuracy_avg = data['Mapping_Correct'].mean()
days_to_reserve_avg = data['Days_to_Reserve'].mean()

st.metric("Reserve Timeliness (%)", f"{reserve_timely_avg:.2f}")
st.metric("Mapping Accuracy (%)", f"{mapping_accuracy_avg:.2f}")
st.metric("Average Days to Reserve", f"{days_to_reserve_avg:.2f} days")

# Bar Charts for Regions
st.subheader("Reserve Timeliness by Region")
st.bar_chart(data.set_index("Claim Prov")['Reserve_Timely'])

st.subheader("Mapping Accuracy by Region")
st.bar_chart(data.set_index("Claim Prov")['Mapping_Correct'])

# Histogram for Days to Reserve
st.subheader("Distribution of Days to Reserve")
fig, ax = plt.subplots()
ax.hist(data['Days_to_Reserve'].dropna(), bins=30, color='skyblue', edgecolor='black')
ax.axvline(7, color='red', linestyle='dashed', linewidth=2, label="7-Day Standard")
plt.legend()
st.pyplot(fig)

# Upload Option
st.subheader("Upload New Data")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    new_data = pd.read_excel(uploaded_file)
    st.write(new_data)
