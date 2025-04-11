import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Green IT Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("server/app/merged_data.csv")  # Replace with your actual CSV file

df = load_data()

# Title
st.title("🌿 Green IT Dashboard")

# KPIs
# Bar Chart: Total Power Consumption Over Time
#change y to mac_address.....
st.subheader("⚡ Energy Consumption per pc")

fig_energy = px.bar(df, x="cpu_usage", y="total_power", 
                    labels={"cpu_usage": "CPU Usage (%)", "total_power": "Power Consumption (kWh)"},
                    color="total_power",
                    color_continuous_scale="reds")

# Adjust layout to control bar width
fig_energy.update_layout(
    bargap=0.02,  # Reduces space between bars
    bargroupgap=0.01,  # Reduces space between grouped bars
    height=500,  # Adjust for better visualization
    width=800 if len(df) < 10 else None,  # Keep width large if fewer data points
)

st.plotly_chart(fig_energy, use_container_width=True)

#bar graph for same
#change y to mac_address.....
st.subheader("⚡ Energy Consumption per pc")

fig_pie = px.pie(df, values="total_power", names=df["cpu_usage"],  
                 color_discrete_sequence=px.colors.sequential.Greens)  # Contrast color scheme

# Improve layout
fig_pie.update_traces(textinfo='percent+label', pull=[0.05]*len(df))  # Slightly separate slices

st.plotly_chart(fig_pie, use_container_width=True)


# Line Chart: Trends over Time
st.subheader("📈 CPU, RAM & Disk Usage Over Time")
fig_line = px.line(df, x="timestamp", y=["cpu_usage", "memory_usage", "disk_usage"],
                   labels={"value": "Usage (%)", "variable": "Resource"},
                   title="System Resource Utilization")
st.plotly_chart(fig_line, use_container_width=True)


# Footer
st.markdown("Developed for **Sustainable IT Monitoring** ✅")


##Iffat code....

# import streamlit as st
# import pandas as pd
# import plotly.express as px

# # Set Page Title
# st.set_page_config(page_title="Green IT Dashboard", layout="wide")

# # Title
# st.markdown("<h1 style='text-align: center; color: red;'>Tech Mahindra Green IT Dashboard</h1>", unsafe_allow_html=True)

# # Metrics
# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Hosts", "27")
# col2.metric("Total Energy Consumption", "16.6304 kWh")
# col3.metric("Total CO2 Emission", "0.0031 kg CO2")
# col4.metric("Critical Hosts", "4", delta="↑2", delta_color="inverse")

# # System Stats
# col5, col6 = st.columns(2)
# with col5:
#     st.subheader("System Stats")
#     st.write("CPU: 747.70")
#     st.write("Disk: 76.00")
#     st.write("RAM: 6907.10")
#     st.write("Network: 958834.00")

# with col6:
#     st.subheader("Alerts")
#     st.write("⚠ e257hdA4J8p - Disk Issue")

# # Sample Data for Graphs
# data = {
#     "Host": [f"Host{i}" for i in range(1, 9)],
#     "Energy Consumption": [5.5, 6.2, 4.8, 5.1, 7.0, 6.5, 4.3, 5.8],
#     "CO2 Emission": [0.001, 0.002, 0.0012, 0.0015, 0.0022, 0.002, 0.001, 0.0018]
# }

# df = pd.DataFrame(data)

# # Energy Consumption Bar Chart
# fig_energy = px.bar(df, x="Energy Consumption", y="Host", orientation="h", title="Energy Consumption", color="Energy Consumption")
# st.plotly_chart(fig_energy, use_container_width=True)

# # CO2 Emission Bar Chart
# fig_co2 = px.bar(df, x="CO2 Emission", y="Host", orientation="h", title="CO2 Emission", color="CO2 Emission")
# st.plotly_chart(fig_co2, use_container_width=True)

# # Pie Chart for Energy Consumption
# fig_pie = px.pie(df, values="Energy Consumption", names="Host", title="Energy Consumption Distribution")
# st.plotly_chart(fig_pie, use_container_width=True)

###############

# import streamlit as st
# import pandas as pd
# import plotly.express as px

# # Set page title and layout
# st.set_page_config(page_title="Green IT Dashboard", layout="wide")

# # Function to create a colored block
# def colored_block(title, value, color):
#     st.markdown(
#         f"""
#         <div style="
#             background-color: {color}; 
#             padding: 15px; 
#             border-radius: 10px; 
#             text-align: center;
#             color: white;
#             font-size: 20px;
#             font-weight: bold;">
#             {title}<br> <span style="font-size: 28px;">{value}</span>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# # Title
# st.markdown("<h1 style='text-align: center; color: red;'>Tech Mahindra Green IT Dashboard</h1>", unsafe_allow_html=True)

# # Metrics Section
# col1, col2, col3, col4 = st.columns(4)
# with col1:
#     colored_block("Hosts", "27", "#4CAF50")  # Green
# with col2:
#     colored_block("Total Energy Consumption", "16.6304 kWh", "#2196F3")  # Blue
# with col3:
#     colored_block("Total CO2 Emission", "0.0031 kg CO2", "#FF9800")  # Orange
# with col4:
#     colored_block("Critical Hosts", "4", "#F44336")  # Red

# # Resource Usage Section
# st.markdown("### Resource Usage")
# col5, col6, col7, col8 = st.columns(4)
# with col5:
#     colored_block("CPU", "747.70", "#673AB7")  # Purple
# with col6:
#     colored_block("Disk", "76.00", "#3F51B5")  # Indigo
# with col7:
#     colored_block("RAM", "6907.10", "#009688")  # Teal
# with col8:
#     colored_block("Network", "958834.00", "#FF5722")  # Deep Orange

# # Alerts Section
# st.markdown("### Alerts")
# st.markdown(
#     """
#     <div style="background-color: #E53935; padding: 15px; border-radius: 10px; color: white; font-size: 18px;">
#         ⚠ e257na4Ad9: Disk issue detected
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# # Sample Data for Energy Consumption
# energy_data = pd.DataFrame({
#     "Host": [f"Host-{i}" for i in range(1, 8)],
#     "Energy Consumption (kWh)": [5.2, 4.8, 3.6, 6.1, 7.3, 2.9, 4.5]
# })

# # Energy Consumption Bar Chart
# st.markdown("### Energy Consumption")
# fig_energy = px.bar(energy_data, x="Energy Consumption (kWh)", y="Host", orientation='h', color="Energy Consumption (kWh)", color_continuous_scale="greens")
# st.plotly_chart(fig_energy, use_container_width=True)

# # Sample Data for CO2 Emission
# co2_data = pd.DataFrame({
#     "Host": [f"Host-{i}" for i in range(1, 5)],
#     "CO2 Emission (kg CO2)": [0.0021, 0.0018, 0.0027, 0.0015]
# })

# # CO2 Emission Bar Chart
# st.markdown("### CO2 Emission")
# fig_co2 = px.bar(co2_data, x="CO2 Emission (kg CO2)", y="Host", orientation='h', color="CO2 Emission (kg CO2)", color_continuous_scale="blues")
# st.plotly_chart(fig_co2, use_container_width=True)