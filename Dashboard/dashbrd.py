# import streamlit as st
# import pandas as pd
# import redis
# import io
# from streamlit_autorefresh import st_autorefresh

# # --- Configuration ---
# REDIS_HOST = 'heroic-jawfish-62360.upstash.io'
# REDIS_PORT = 6379
# REDIS_PASSWORD = 'AfOYAAIjcDEzMzM1NTgyNTQ4YTM0NzQ0YjMzODU2NDlhNTM5YzY2MXAxMA'
# REDIS_KEY = 'merged_csv'

# # --- Redis Connection ---
# redis_client = redis.Redis(
#     host=REDIS_HOST,
#     port=REDIS_PORT,
#     password=REDIS_PASSWORD,
#     ssl=True,
#     decode_responses=True
# )

# # --- Page Setup ---
# st.set_page_config(page_title="Live CO₂ Dashboard", layout="wide")
# st.title("📊 Real-Time CO₂ Monitoring Dashboard")
# st.markdown("This dashboard auto-refreshes every 5 seconds to display live data from Redis.")

# # --- Auto-refresh every 5 seconds ---
# st_autorefresh(interval=600000, key="data_refresh")

# # --- Fetch CSV from Redis ---
# csv_data = redis_client.get(REDIS_KEY)

# if csv_data:
#     df = pd.read_csv(io.StringIO(csv_data))

#     st.success("✅ Live data fetched from Redis!")

#     # --- Display Data Table ---
#     with st.expander("🔍 View Raw Data"):
#         st.dataframe(df)

#     # --- Display a Sample Chart ---
#     col1, col2 = st.columns(2)

#     with col1:
#         if 'CPU_Usage' in df.columns and 'Timestamp' in df.columns:
#             st.subheader("⚙️ CPU Usage Over Time")
#             st.line_chart(data=df, x="Timestamp", y="CPU_Usage")

#     with col2:
#         if 'CO2_Emission' in df.columns and 'Timestamp' in df.columns:
#             st.subheader("🌿 CO₂ Emission Over Time")
#             st.line_chart(data=df, x="Timestamp", y="CO2_Emission")

# else:
#     st.warning("⚠️ No data found in Redis. Waiting for new data...")
import streamlit as st
import pandas as pd
import requests
import io

# Title
st.title("Real-time System Insights Dashboard")

# Fetch CSV data from API
@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_data():
    url = "https://be-project-client-server.onrender.com/download-csv-insights"
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = response.content
        df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
        return df
    else:
        st.error("Failed to fetch data from API.")
        return pd.DataFrame()

# Load data
df = fetch_data()

if not df.empty:
    st.subheader("Live Data Table")
    st.dataframe(df)

    # Visualize CPU, Memory, and Disk usage
    st.subheader("Resource Usage Overview")
    st.line_chart(df[['cpu_usage', 'memory_usage', 'disk_usage']])

    # Show Carbon Emissions vs Power
    st.subheader("Power vs Carbon Emission")
    st.line_chart(df[['total_power', 'carbon emission']])
else:
    st.warning("No data available yet.")
