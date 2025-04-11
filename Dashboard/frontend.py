import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
import requests  # Also fix for second error
import io

# MUST be the first Streamlit command
st.set_page_config(page_title="ESG Tracker", layout="wide")

# --- Styling ---
st.markdown("""
    <style>
        .main, .block-container {
            padding: 1rem 2rem;
            background-color: #ffffff;
        }
        .sidebar .sidebar-content {
            background-color: ##00004B;
        }
        .stButton>button {
            background-color: #FFFFFF;
            color: #38A889;
            border: 1px solid #38A889;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #38A889;
            color: white;
        }
        .esg-card {
            background-color: #ffffff;
            padding: 1rem;
            border-left: 6px solid #6C63FF;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.image("wmremove-transformed.jpeg", width=280)  # Logo Placeholder
st.sidebar.markdown("## 📚 Navigation")
nav_items = [
    "Dashboard", "Analytics", "ESG", "Suppliers", "Advisory",
    "Facilities", "Goals", "Credible AskESG", "Documents", "Reports", "Settings"
]
for item in nav_items:
    st.sidebar.button(item)

# --- Title Section ---
st.title("🌍 ESG Tracker Dashboard")
st.markdown("Get real-time insights on energy usage, emissions, and governance.")

# --- Top Summary Cards ---
st.markdown("### 🔍 Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Hosts", value="4")
with col2:
    st.metric(label="Total Energy (kWh)", value="234")
with col3:
    st.metric(label="Total CO₂ Emission (kg)", value="178")
with col4:
    st.metric(label="Critical Hosts", value="2")

style_metric_cards(
    background_color="#f8f9fc",
    border_left_color="#6C63FF",
    border_color="#e0e0e0"
)

# --- Alerts Section ---
st.markdown("### 🚨 Alerts")
with st.container():
    st.markdown("""
    <div class="esg-card">
        <strong>🔴 2 Critical Hosts Detected</strong><br>
        <small>High energy usage and carbon emission from Host-PC-2 and Host-PC-3.</small><br>
        <small>Suggested Action: Investigate background processes and cooling efficiency.</small>
    </div>
    """, unsafe_allow_html=True)

# --- ESG Summary Dropdowns ---
st.markdown("### 🧭 ESG Summary")

esg_factors = {
    "Environmental": {
        "definition": "Measures emissions, energy use, waste management, etc.",
        "parameters": ["CO2 Emissions", "Power Consumption", "CPU Usage", "Processes"],
    },
    "Social": {
        "definition": "Captures employee well-being, digital usage ethics, etc.",
        "parameters": ["User Access Logs", "HR Guidelines"],
    },
    "Governance": {
        "definition": "Covers data integrity, transparency, security policies.",
        "parameters": ["Audit Logs", "Software License Validity", "Policy Compliance"],
    },
}

for i, (factor, content) in enumerate(esg_factors.items()):
    with st.expander(f"📂 {factor}"):
        st.write(f"**Definition:** {content['definition']}")
        st.write("**Parameters Used:**")
        st.write(", ".join(content['parameters']))
        st.button(f"🔽 View {factor} Analysis", key=f"view_{factor.lower()}")

# --- Detailed ESG Sections ---
st.markdown("---")
st.markdown("## 📊 ESG Detailed Analysis")

# Environmental Section
st.markdown("### ♻️ Environmental Analysis")
st.metric("Environmental Score", "76 / 100")
st.markdown("**Insights:**")
st.write("High CO₂ output observed during peak hours. Optimize scheduling and resource use.")

# --- Fetch Real-time CSV Data from API ---
@st.cache_data(ttl=60)
def fetch_data():
    url = "http://be-project-client-server.onrender.com/download-csv-individual"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            df.dropna(how="all", inplace=True)
            return df
        else:
            st.error(f"Failed to fetch data: Status code {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Load data
df = fetch_data()

# Convert timestamp if available
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])

# Show warning if data is empty
if df.empty:
    st.warning("No data available to display.")
    st.stop()

# ------------------ GRAPH 1: Bar chart of Total Power by Device ------------------
if {"mac_address", "total_power"}.issubset(df.columns):
    fig_bar = px.bar(
        df,
        y="mac_address",
        x="total_power",
        orientation="h",
        title="Total Power Consumption by the Device",
        color="total_power",
        color_continuous_scale="reds"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ------------------ GRAPH 2: Pie chart of Carbon Emission by Device ------------------
if {"mac_address", "carbon emission"}.issubset(df.columns):
    fig_pie = px.pie(
        df,
        names="mac_address",
        values="carbon emission",
        title="Total Carbon Emission by Device",
        color_discrete_sequence=px.colors.sequential.Greens
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ------------------ GRAPH 3: Line chart of Carbon Emission over Time ------------------
if {"timestamp", "carbon emission"}.issubset(df.columns):
    fig_line = px.line(
        df,
        x="timestamp",
        y="carbon emission",
        title="Carbon Emission Over Time",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#1f77b4"]
    )
    fig_line.update_layout(xaxis_title="Timestamp", yaxis_title="Carbon Emission")
    st.plotly_chart(fig_line, use_container_width=True)

# ------------------ GRAPH 4: Heatmap of Resource Usage Correlation ------------------
from sklearn.preprocessing import MinMaxScaler
heatmap_cols = ["carbon emission", "cpu_usage", "memory_usage", "disk_usage", "network_usage"]
if set(heatmap_cols).issubset(df.columns):
    heatmap_df = df[heatmap_cols].copy()
    scaler = MinMaxScaler()
    heatmap_scaled = pd.DataFrame(scaler.fit_transform(heatmap_df), columns=heatmap_df.columns)
    corr_matrix = heatmap_scaled.corr()

    fig_heatmap = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="Blues",
        title="Heatmap: Correlation Between Resources and Carbon Emission"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ------------------ GRAPH 5: Multi-line Graph of Resource Usage Over Time ------------------
import plotly.subplots as sp
import plotly.graph_objects as go
resource_cols = {"timestamp", "cpu_usage", "memory_usage", "network_usage"}
if resource_cols.issubset(df.columns):
    fig = sp.make_subplots(rows=3, cols=1, shared_xaxes=True,
                           subplot_titles=("CPU Usage", "Memory Usage", "Network Usage"))

    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["cpu_usage"],
                             mode='lines+markers', name='CPU Usage', line=dict(color="#636EFA")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["memory_usage"],
                             mode='lines+markers', name='Memory Usage', line=dict(color="#00CC96")), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["network_usage"],
                             mode='lines+markers', name='Network Usage', line=dict(color="#AB63FA")), row=3, col=1)

    fig.update_layout(height=800, title_text="Resource Usage Over Time (Separate Views)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.title("Environmental Insights")

# Fetch data
url = "https://be-project-client-server.onrender.com/download-csv-insights"
response = requests.get(url)

if response.status_code == 200:
    data = pd.read_csv(io.StringIO(response.text))

    if not data.empty:
        last_row = data.tail(1).to_dict(orient='records')[0]

        name_mapping = {
            "device_total_ram": "Total Device RAM (GB)",
            "cpu_usage": "CPU Usage (%)",
            "memory_usage": "Memory Usage (%)",
            "disk_usage": "Disk Usage (%)",
            "total_power": "Total Power Consumption (W)",
            "carbon emission": "Carbon Emission (gCO₂)",
            "network_usage": "Network Usage (MB/s)",
            "grid_intensity": "Grid Intensity (gCO₂/kWh)",
            "num_processes": "Number of Running Processes",
            "predicted_power": "Predicted Power Consumption (W)",
            "predicted_co2": "Predicted Carbon Emission (gCO₂)",
            "optimal_cpu": "Suggested Optimal CPU Usage (%)",
            "optimized_co2": "Optimized Carbon Emission (gCO₂)",
            "co2_reduction_%": "CO₂ Reduction (%)"
        }

        # 📊 Section: Summary using Expanders and Columns
        st.subheader("Summary")

        with st.expander("🖥 System Information"):
            cols = st.columns(2)
            cols[0].markdown(f"{name_mapping['device_total_ram']}: {round(last_row['device_total_ram'], 2)}")
            cols[1].markdown(f"{name_mapping['num_processes']}: {round(last_row['num_processes'], 2)}")

        with st.expander("📈 Usage Statistics"):
            cols = st.columns(2)
            cols[0].markdown(f"{name_mapping['cpu_usage']}: {round(last_row['cpu_usage'], 2)}")
            cols[1].markdown(f"{name_mapping['memory_usage']}: {round(last_row['memory_usage'], 2)}")
            cols = st.columns(2)
            cols[0].markdown(f"{name_mapping['disk_usage']}: {round(last_row['disk_usage'], 2)}")
            cols[1].markdown(f"{name_mapping['network_usage']}: {round(last_row['network_usage'], 2)}")

        with st.expander("⚡ Power and Emissions"):
            cols = st.columns(2)
            cols[0].markdown(f"{name_mapping['total_power']}: {round(last_row['total_power'], 2)}")
            cols[1].markdown(f"{name_mapping['carbon emission']}: {round(last_row['carbon emission'], 2)}")
            cols = st.columns(2)
            cols[0].markdown(f"{name_mapping['grid_intensity']}: {round(last_row['grid_intensity'], 2)}")

        with st.expander("🤖 Predictions and Optimization"):
            cols = st.columns(2)
            cols[0].markdown(f"{name_mapping['predicted_power']}: {round(last_row['predicted_power'], 2)}")
            cols[1].markdown(f"{name_mapping['predicted_co2']}: {round(last_row['predicted_co2'], 2)}")
            cols = st.columns(2)
            cols[0].markdown(f"{name_mapping['optimal_cpu']}: {round(last_row['optimal_cpu'], 2)}")
            cols[1].markdown(f"{name_mapping['optimized_co2']}: {round(last_row['optimized_co2'], 2)}")
            cols = st.columns(1)
            cols[0].markdown(f"{name_mapping['co2_reduction_%']}: {round(last_row['co2_reduction_%'], 2)}%")   
            
   

st.title("📊 Device-Wise Environmental Impact Analysis")

# Fetch data from individual API
url = "https://be-project-client-server.onrender.com/download-csv-individual"
response = requests.get(url)

if response.status_code == 200:
    data = pd.read_csv(io.StringIO(response.text))

    if not data.empty and 'mac_address' in data.columns and 'carbon emission' in data.columns and 'timestamp' in data.columns:

        # Convert timestamp to datetime
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['hour'] = data['timestamp'].dt.hour

        # Start tabs
        tab01, tab02, tab03, tab04, tab06 = st.tabs([
            "🔥 Peak Carbon Emitters",
            "⏰ Peak Emission Hours",
            "⚖ Efficiency Scores",
            "🔎 Underutilized but Consuming",
            # "🧟 Zombie Processes",
            "🔍 Device Comparison"
        ])

        with tab01:
            st.subheader("🔥 Peak Carbon Emitters")
            top_emitters = data.groupby("mac_address")['carbon emission'].sum().sort_values(ascending=False).head(5)
            st.write("These devices emitted the most carbon over time:")
            st.dataframe(top_emitters.reset_index().rename(columns={'carbon emission': 'Total Emission (gCO₂)'}))

        with tab02:
            st.subheader("⏰ Peak Emission Hours")
            hourly_emission = data.groupby("hour")['carbon emission'].mean().sort_values(ascending=False)
            st.write("Average emissions per hour:")
            st.dataframe(hourly_emission.reset_index().rename(columns={'hour': 'Hour of Day', 'carbon emission': 'Avg Emission (gCO₂)'}))

        with tab03:
            st.subheader("⚖ Device Efficiency Scores")
            efficiency = data.groupby("mac_address").apply(lambda x: x['carbon emission'].sum() / x['total_power'].sum() if x['total_power'].sum() > 0 else float('inf'))
            efficiency_df = efficiency.sort_values().reset_index()
            efficiency_df.columns = ['MAC Address', 'gCO₂ per Watt']
            st.write("Lower values are better:")
            st.dataframe(efficiency_df)

        with tab04:
            st.subheader("🔎 Underutilized but Consuming")
            underutilized = data[(data['cpu_usage'] < 20) & (data['total_power'] > 5)]
            st.write("Devices consuming power but barely doing work:")
            st.dataframe(underutilized[['mac_address', 'cpu_usage', 'total_power', 'carbon emission']])

        # with tab05:
        #     st.subheader("🧟 Zombie Processes")
        #     zombie_processes = data[(data['num_processes'] > 100) & (data['cpu_usage'] < 10)]
        #     st.write("Devices with high number of processes but low CPU usage:")
        #     st.dataframe(zombie_processes[['mac_address', 'num_processes', 'cpu_usage']])

        with tab06:
            st.subheader("🔍 Device Comparison")
            selected_macs = st.multiselect("Select MAC addresses to compare:", data['mac_address'].unique())
            if selected_macs:
                comparison = data[data['mac_address'].isin(selected_macs)]
                avg_comparison = comparison.groupby("mac_address")[['cpu_usage', 'memory_usage', 'disk_usage', 'total_power', 'carbon emission']].mean().reset_index()
                st.dataframe(avg_comparison.rename(columns={
                    'cpu_usage': 'Avg CPU (%)',
                    'memory_usage': 'Avg Memory (%)',
                    'disk_usage': 'Avg Disk (%)',
                    'total_power': 'Avg Power (W)',
                    'carbon emission': 'Avg CO₂ (gCO₂)'
                }))

        # Recommendations section using cards
        st.markdown("## 🌿 What You Can Do")

        rec1, rec2, rec3 = st.columns(3)

        with rec1:
            with st.container(border=True):
                st.markdown("### 🔌 Power Down Idle Devices")
                st.write("Shut down or sleep devices not in use to save energy.")
            with st.container(border=True):
                st.markdown("### 🌐 Prefer Green Cloud Providers")
                st.write("Use cloud regions powered by renewable energy.")
            with st.container(border=True):
                st.markdown("### 📶 Reduce Network Usage")
                st.write("Avoid unnecessary data syncs to save bandwidth and energy.")

        with rec2:
            with st.container(border=True):
                st.markdown("### ⚙ Use Efficient Hardware")
                st.write("Opt for energy-saving CPUs and SSDs to reduce consumption.")
            with st.container(border=True):
                st.markdown("### 🌙 Schedule Heavy Tasks Smartly")
                st.write("Run power-intensive tasks during off-peak hours.")
            with st.container(border=True):
                st.markdown("### 🛑 Kill Zombie Processes")
                st.write("Eliminate resource-hogging background processes.")

        with rec3:
            with st.container(border=True):
                st.markdown("### 🧠 Optimize CPU Usage")
                st.write("Reduce background tasks and optimize processing.")
            with st.container(border=True):
                st.markdown("### 📤 Auto Scale When Needed")
                st.write("Dynamically scale services based on demand.")
            with st.container(border=True):
                st.markdown("### ♻ Enable Dark Mode & Battery Saver")
                st.write("Helps reduce device power usage across the board.")

    else:
        st.error("MAC address, timestamp, or carbon emission data not available in the dataset.")
else:
    st.error("Failed to fetch data from the API.")

# # Social Section
# st.markdown("---")
# st.markdown("### 🤝 Social Analysis")
# st.metric("Social Score", "84 / 100")

# # Governance Section
# st.markdown("---")
# st.markdown("### 🏛 Governance Analysis")
# st.metric("Governance Score", "91 / 100")

st.title("📰 News on Sustainable Development")



API_TOKEN = "afc04c45a9cc8098742d02b8b9f5d423"  # Replace this with your actual API key
BASE_URL = "https://gnews.io/api/v4/search"


# query = st.text_input("Search News", value="sustainable development OR ESG")
params = {
    "q": "sustainable development OR carbon emission OR green IT OR ESG OR climate change",
    "lang": "en",
    "max": 9,
    "token": API_TOKEN
}


# Fetch data
response = requests.get(BASE_URL, params=params)


# Fetch data
response = requests.get(BASE_URL, params=params)


import streamlit.components.v1 as components
if response.status_code == 200:
    articles = response.json().get("articles", [])

    html_content = """
    <style>
    .scrolling-wrapper {
        overflow-x: auto;
        display: flex;
        flex-wrap: nowrap;
        gap: 20px;
        padding-bottom: 1rem;
    }
    .card {
        flex: 0 0 auto;
        width: 300px;
        background-color: #f9f9f9;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        padding: 1rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .card h4 {
        font-size: 1rem;
        margin: 0 0 0.3rem 0;
        height: 3rem;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    .card p {
        font-size: 0.9rem;
        color: #333;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        margin-bottom: 0.5rem;
    }
    .card a {
        text-decoration: none;
        color: #0066cc;
        font-weight: bold;
    }
    </style>
    <div class="scrolling-wrapper">
    """

    for article in articles:
        image_url = article["image"] or "https://via.placeholder.com/300x200"
        title = article["title"]
        description = article["description"] or "No description available."
        source = article["source"]["name"]
        date = article["publishedAt"][:10]
        url = article["url"]

        html_content += f"""
        <div class="card">
            <img src="{image_url}" alt="news image">
            <h4>{title}</h4>
            <p><i>{source} | {date}</i></p>
            <p>{description[:120]}...</p>
            <a href="{url}" target="_blank">Read more</a>
        </div>
        """

    html_content += "</div>"

    components.html(html_content, height=480, scrolling=True)

else:
    st.error("Failed to fetch news. Please check your API token or internet connection.")
