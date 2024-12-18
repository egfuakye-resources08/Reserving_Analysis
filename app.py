import pandas as pd
import streamlit as st
import plotly.express as px

# Set a page title
st.title("Claims Technical Analyst KPI Dashboard")

# --- Data Loading and Cleaning ---
file_path = "Claims Technical Analyst Assessment Data.xlsx"

# Load the file while skipping the first 4 rows
claims_data = pd.read_excel(file_path, sheet_name=0, skiprows=4, engine="openpyxl")

# Clean column names
claims_data.columns = claims_data.columns.str.strip()

# Convert date columns
claims_data['Loss Date'] = pd.to_datetime(claims_data['Loss Date'], errors='coerce')
claims_data['Reserve Transaction Date'] = pd.to_datetime(claims_data['Reserve Transaction Date'], errors='coerce')

# Reserve Mapping Dictionary
reserve_mapping = {
    "Animal (all)": "SC-Other Comp",
    "Coll (all but Hit & Run)": "S1-Collision",
    "Coll-Hit & Run": "SC-Other Comp",
    "Comp-Fire/Entire Vehicle": "S4-Fire/Lightning/Explosion",
    "Comp-Fire/Partial": "S4-Fire/Lightning/Explosion",
    "Comp-Hail": "S7-Hail",
    "Comp-Mechanical Failure": "SC-Other Comp",
    "Comp-Other": "SC-Other Comp",
    "Comp-Rodent": "SC-Other Comp",
    "Comp-Submerged/Flooding": "SC-Other Comp",
    "Comp-Vandlsm/Malicious Dmg": "SA-Malicious Mischief/Vandalism",
    "Comp-Windstorm": "S6-Wind/Tornado/Cyclone",
    "Road Hazard Glass (both)": "S3-Road Hazard Glass",
    "Theft (all)": "SH-Theft of Entire Vehicle",
}

# Calculate derived metrics
claims_data['Days_to_Reserve'] = (claims_data['Reserve Transaction Date'] - claims_data['Loss Date']).dt.days
claims_data['Reserve_Timely'] = claims_data['Days_to_Reserve'] <= 7
claims_data['Mapped Reserve'] = claims_data['Accident Circumstance'].map(reserve_mapping)
claims_data['Mapping_Correct'] = claims_data['Claim Cover'] == claims_data['Mapped Reserve']

# KPI Calculations by Region
kpi_summary = claims_data.groupby("Claim Prov").agg({
    'Reserve_Timely': 'mean',
    'Mapping_Correct': 'mean',
    'Days_to_Reserve': 'mean'
}).reset_index()

# Convert to percentages where applicable
kpi_summary['Reserve_Timely'] *= 100
kpi_summary['Mapping_Correct'] *= 100

# Compute Overall Baseline Performance (across all regions)
overall_reserve_timely = claims_data['Reserve_Timely'].mean() * 100
overall_mapping_correct = claims_data['Mapping_Correct'].mean() * 100
overall_days_to_reserve = claims_data['Days_to_Reserve'].mean()

# Display summary metrics at the top
st.subheader("Overall Baseline Performance")
col1, col2, col3 = st.columns(3)
col1.metric("Reserve Timeliness (%)", f"{overall_reserve_timely:.1f}%")
col2.metric("Mapping Accuracy (%)", f"{overall_mapping_correct:.1f}%")
col3.metric("Avg Days to Reserve", f"{overall_days_to_reserve:.1f}")

# Targets
target_reserve_timely = 90
target_mapping_correct = 95
target_days_to_reserve = 7

# Show the Overall Baseline Performance Bar Chart right after the baseline figures
baseline_data = pd.DataFrame({
    'Metric': ['Reserve Timeliness (%)', 'Mapping Accuracy (%)', 'Avg Days to Reserve'],
    'Value': [overall_reserve_timely, overall_mapping_correct, overall_days_to_reserve]
})

fig = px.bar(
    baseline_data,
    x='Value',
    y='Metric',
    orientation='h',
    title="Overall Baseline Performance (Detailed)",
    text='Value',
    color='Metric',
    color_discrete_sequence=['#4C72B0', '#55A868', '#C44E52']
)
fig.update_traces(
    texttemplate='%{text:.1f}' + baseline_data['Metric'].apply(lambda x: '%' if '(%)' in x else '').tolist()[0],
    textposition='inside'
)
fig.update_layout(
    yaxis={'categoryorder':'array', 'categoryarray':['Reserve Timeliness (%)', 'Mapping Accuracy (%)', 'Avg Days to Reserve']}
)
fig.update_xaxes(range=[0, baseline_data['Value'].max()*1.1], title="Value")
fig.update_yaxes(title="")
st.plotly_chart(fig, use_container_width=True)

# Now show the KPI Summary by Region and other charts
st.subheader("KPI Summary by Region")
st.dataframe(kpi_summary)

# Sidebar Filters
st.sidebar.title("Filters")
selected_region = st.sidebar.selectbox("Select Region", options=["All"] + kpi_summary['Claim Prov'].tolist())

# Filter data based on selection
if selected_region != "All":
    plot_data = kpi_summary[kpi_summary['Claim Prov'] == selected_region].copy()
else:
    plot_data = kpi_summary.copy()

# 1. Reserve Timeliness by Region
st.subheader("Reserve Timeliness by Region")
fig = px.line(plot_data, x='Claim Prov', y='Reserve_Timely', markers=True, title="Reserve Timeliness by Region")
fig.add_hline(y=target_reserve_timely, line_dash="dash", line_color="red", annotation_text=f"Target: {target_reserve_timely}%", annotation_position="top left")
fig.update_traces(texttemplate='%{y:.1f}%', textposition='top center', mode='markers+lines+text')
fig.update_yaxes(title="Reserve Timeliness (%)")
fig.update_xaxes(title="Region")
st.plotly_chart(fig, use_container_width=True)

# 2. Mapping Accuracy by Region
st.subheader("Mapping Accuracy by Region")
fig = px.line(plot_data, x='Claim Prov', y='Mapping_Correct', markers=True, title="Mapping Accuracy by Region", color_discrete_sequence=['#55A868'])
fig.add_hline(y=target_mapping_correct, line_dash="dash", line_color="red", annotation_text=f"Target: {target_mapping_correct}%", annotation_position="top left")
fig.update_traces(texttemplate='%{y:.1f}%', textposition='top center', mode='markers+lines+text')
fig.update_yaxes(title="Mapping Accuracy (%)")
fig.update_xaxes(title="Region")
st.plotly_chart(fig, use_container_width=True)

# 3. Average Days to Reserve by Region
st.subheader("Average Days to Reserve by Region")
fig = px.line(plot_data, x='Claim Prov', y='Days_to_Reserve', markers=True, title="Average Days to Reserve by Region", color_discrete_sequence=['#C44E52'])
fig.add_hline(y=target_days_to_reserve, line_dash="dash", line_color="blue", annotation_text=f"Target: {target_days_to_reserve} Days", annotation_position="top left")
fig.update_traces(texttemplate='%{y:.1f}', textposition='top center', mode='markers+lines+text')
fig.update_yaxes(title="Average Days to Reserve")
fig.update_xaxes(title="Region")
st.plotly_chart(fig, use_container_width=True)

# Heatmap of KPI (Interactive via Plotly)
st.subheader("Regional KPI Heatmap")
heatmap_data = kpi_summary.set_index('Claim Prov')[['Reserve_Timely', 'Mapping_Correct', 'Days_to_Reserve']]

fig = px.imshow(
    heatmap_data,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    color_continuous_scale='Greens',
    aspect='auto',
    title="Regional KPI Heatmap"
)
fig.update_xaxes(title="KPI Metrics")
fig.update_yaxes(title="Region")

# Add annotation for targets
fig.add_annotation(
    x=0.5, y=-0.2,
    text=f"Targets: Reserve Timely ≥ {target_reserve_timely}%, Mapping Correct ≥ {target_mapping_correct}%, Days ≤ {target_days_to_reserve}",
    showarrow=False,
    xref='paper',
    yref='paper',
    font=dict(size=10),
    xanchor='center',
    yanchor='top'
)

st.plotly_chart(fig, use_container_width=True)

st.write("All plots are now interactive. Use the sidebar filters to customize your view!")
