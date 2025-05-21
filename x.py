import streamlit as st
import pandas as pd
import plotly.express as px


# Use password from secrets
PASSWORD = st.secrets["general"]["password"]

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect password")
        st.stop()

check_password()

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    file_path = "KA Report.xlsx"
    df = pd.read_excel(file_path, sheet_name='Hub wise KA', header=[2, 3])

    # Flatten and clean MultiIndex column names
    df.columns = [f"{a.strip()} - {b.strip()}" if b.strip() else a.strip() for a, b in df.columns]

    # Rename the Hub Name column
    df.rename(columns={col: 'Hub Name' for col in df.columns if 'Hub Name' in col}, inplace=True)

    return df

# Load data
hub_df = load_data()

# Define metrics and display names
metrics = {
    "DF Count": "Deep Freezer Count",
    "Secondary Booking": "Secondary Booking",
    "Throughput": "Throughput",
    "Primary": "Primary",
    "Distributor Storeage DF Count": "Distributor Storage",
    "MKT CREDIT": "Market Credit",
    "DB CLSOING STOCK": "Distributor Closing Stock"
}

# Metric selection
st.title("Karnataka Regional Performance Dashboard")
selected_metric = st.selectbox("Select Metric", list(metrics.keys()), format_func=lambda x: metrics[x])

# Construct column names for plotting
fy24_col = f"{selected_metric} - FY-24"
fy25_col = f"{selected_metric} - FY-25"

# Bar Charts
col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(hub_df, x='Hub Name', y=fy24_col, title=f"FY-24 {metrics[selected_metric]}")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(hub_df, x='Hub Name', y=fy25_col, title=f"FY-25 {metrics[selected_metric]}")
    st.plotly_chart(fig2, use_container_width=True)

# YOY Growth
hub_df['GOLY'] = (hub_df[fy25_col] - hub_df[fy24_col]) / hub_df[fy24_col]
fig3 = px.bar(hub_df, x='Hub Name', y='GOLY', title=f"YOY Growth in {metrics[selected_metric]}", labels={'GOLY': 'Growth %'})
st.plotly_chart(fig3, use_container_width=True)

# Map with real hub locations
st.header("Hub Locations in Karnataka")
location_map = {
    'Bangalore': (12.9716, 77.5946),
    'Hubli': (15.3647, 75.1240),
    'Mysore': (12.2958, 76.6394),
    'North Kanara': (14.8015, 74.1240),
    'South Kanara': (12.9141, 74.8560)
}

map_df = pd.DataFrame([
    {"Hub Name": name, "Latitude": lat, "Longitude": lon}
    for name, (lat, lon) in location_map.items()
])

fig_map = px.scatter_mapbox(
    map_df, lat="Latitude", lon="Longitude", hover_name="Hub Name",
    zoom=6, height=400
)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# Key Insights
st.header("Key Insights")
growth_mean = hub_df['GOLY'].mean()
max_hub = hub_df.loc[hub_df['GOLY'].idxmax(), 'Hub Name']
min_hub = hub_df.loc[hub_df['GOLY'].idxmin(), 'Hub Name']

st.markdown(f"- **Average YOY growth in {metrics[selected_metric]} across hubs:** {growth_mean:.2%}")
st.markdown(f"- **Best performing hub:** {max_hub}")
st.markdown(f"- **Least performing hub:** {min_hub}")

# Future Steps
st.header("Future Steps")
st.markdown(f"- Focus support on low-performing hubs like **{min_hub}**")
st.markdown(f"- Replicate strategies from high-performing hubs like **{max_hub}**")
st.markdown("- Evaluate constraints in throughput, storage, and secondary bookings by sub-segment")

st.header("📊 Quarterly Analysis")

# --- Secondary Booking Quarterly Data ---
st.subheader("Secondary Booking (Quarterly)")
secondary_quarterly = {
    'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
    'FY-24': [1178.95, 1437.04, 2053.25, 2755.99],
    'FY-25': [3270.85, 1999.92, 3128.93, 4780.34],
    'GOLY %': [177, 39, 52, 73]
}
df_sec = pd.DataFrame(secondary_quarterly)

col1, col2 = st.columns(2)
with col1:
    fig_sec = px.bar(df_sec, x="Quarter", y=["FY-24", "FY-25"],
                     barmode="group", title="Secondary Booking FY24 vs FY25")
    st.plotly_chart(fig_sec, use_container_width=True)

with col2:
    fig_sec_goly = px.bar(df_sec, x="Quarter", y="GOLY %",
                          color="GOLY %", title="Secondary GOLY % by Quarter",
                          color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_sec_goly, use_container_width=True)


# --- Primary Booking Quarterly Data ---
st.subheader("Primary Booking (Quarterly)")
primary_quarterly = {
    'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
    'FY-24': [3874.93, 1753.31, 2856.52, 3544.10],
    'FY-25': [4177.43, 1776.67, 2986.07, 4126.29],
    'GOLY %': [7.81, 1.33, 4.54, 16.43]
}
df_pri = pd.DataFrame(primary_quarterly)

col3, col4 = st.columns(2)
with col3:
    fig_pri = px.bar(df_pri, x="Quarter", y=["FY-24", "FY-25"],
                     barmode="group", title="Primary Booking FY24 vs FY25")
    st.plotly_chart(fig_pri, use_container_width=True)

with col4:
    fig_pri_goly = px.bar(df_pri, x="Quarter", y="GOLY %",
                          color="GOLY %", title="Primary GOLY % by Quarter",
                          color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_pri_goly, use_container_width=True)

# --- ABC Classification Section ---
st.header("🔠 ABC Classification Based on FY-25 Secondary Booking")

# Ensure the required column exists
sec25_col = "Secondary Booking - FY-25"
if sec25_col in hub_df.columns:
    # Sort hubs by descending Secondary Booking FY25
    abc_df = hub_df[['Hub Name', sec25_col]].copy()
    abc_df.sort_values(by=sec25_col, ascending=False, inplace=True)
    abc_df['Cumulative %'] = abc_df[sec25_col].cumsum() / abc_df[sec25_col].sum() * 100

    # Assign ABC categories
    def assign_abc(cum_pct):
        if cum_pct <= 80:
            return 'A'
        elif cum_pct <= 95:
            return 'B'
        else:
            return 'C'

    abc_df['Category'] = abc_df['Cumulative %'].apply(assign_abc)

    # Display ABC table
    st.dataframe(abc_df[['Hub Name', sec25_col, 'Cumulative %', 'Category']], use_container_width=True)

    # ABC Bar Chart
    fig_abc = px.bar(abc_df, x='Hub Name', y=sec25_col, color='Category',
                     title="ABC Classification - FY-25 Secondary Booking",
                     color_discrete_map={'A': 'green', 'B': 'orange', 'C': 'red'})
    st.plotly_chart(fig_abc, use_container_width=True)
else:
    st.warning("FY-25 Secondary Booking data not found for ABC classification.")


# --- Footer ---
st.markdown("""<hr style="height:1px;border:none;color:#ccc;background-color:#ccc;" />""", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.9em;'>"
    "© 2025 Hangyo Ice Creams Pvt. Ltd. All rights reserved."
    "</div>",
    unsafe_allow_html=True
)
