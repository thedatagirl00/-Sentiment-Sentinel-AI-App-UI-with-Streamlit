import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import os
import pydeck as pdk # Import pydeck

# Force Streamlit to show any startup errors
st.set_page_config(page_title="MediMap Ghana", page_icon="🏥")

# --- MOCK SECURITY SESSION ---
# In a production environment, this would come from a secure OAuth/Auth0 login
if 'staff_id' not in st.session_state:
    st.session_state['staff_id'] = "ST-GH-2024-001"

st.write(f"### 🛠 MediMap System Status: Active | User: {st.session_state['staff_id']}")

try:
    st.title("🏥 MediMap Ghana: AI Bed Management")
    st.markdown("--- ")

    # Verify Model File
    model_path = 'medimap_model.pkl'
    if not os.path.exists(model_path):
        st.error(f"❌ ERROR: Model file '{model_path}' not found!")
        st.stop()

    # Load Model
    model = joblib.load(model_path)

    # Sidebar inputs
    st.sidebar.header("Hospital Input Panel")
    hospital = st.sidebar.selectbox("Target Hospital", ["Korle Bu", "37 Military", "Ridge", "Kasoa General"])
    occupancy = st.sidebar.slider("Current Occupancy (%)\n (0=Empty, 100=Full)", 0, 100, 75) / 100.0
    staff = st.sidebar.number_input("Staff on Duty", 1, 100, 20)
    discharge = st.sidebar.slider("Avg Discharge Rate", 0.0, 1.0, 0.3)
    emergency = st.sidebar.number_input("Emergency Incoming", 0, 50, 5)

    # Features Preparation
    now = datetime.now()
    hosp_map = {"Korle Bu": 101, "37 Military": 102, "Ridge": 103, "Kasoa General": 104}
    h_id = hosp_map[hospital]

    input_row = pd.DataFrame([{
        'current_occupancy': occupancy,
        'staff_on_duty': staff,
        'avg_discharge_rate': discharge,
        'emergency_incoming': emergency,
        'hour': now.hour,
        'day_of_week': now.weekday(),
        'hosp_101': 1 if h_id == 101 else 0,
        'hosp_102': 1 if h_id == 102 else 0,
        'hosp_103': 1 if h_id == 103 else 0,
        'hosp_104': 1 if h_id == 104 else 0
    }])

    cols = ['current_occupancy', 'staff_on_duty', 'avg_discharge_rate', 'emergency_incoming', 'hour', 'day_of_week', 'hosp_101', 'hosp_102', 'hosp_103', 'hosp_104']
    input_row = input_row[cols]

    # Run AI Prediction
    prob = model.predict(input_row)[0]

    # --- SECURITY FRAMEWORK: LOGGING REQUIREMENTS ---
    # In production, these logs would be written to a secure database or CloudWatch
    audit_log = {
        "Staff_ID": st.session_state['staff_id'],
        "Timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "Change_Log": f"{hospital} Status Update: Occupancy {occupancy*100}%, Staff: {staff}",
        "Device_IP": "Captured (Local Gateway)" # In Streamlit, this is handled by server headers
    }

    # UI Display
    c1, c2 = st.columns(2)
    c1.metric("Bed Availability Chance", f"{prob*100:.1f}%")

    # Define hospital coordinates (updated with real values)
    hospital_coords = {
        "Korle Bu": {"latitude": 5.548, "longitude": -0.222},
        "37 Military": {"latitude": 5.5928, "longitude": -0.1855},
        "Ridge": {"latitude": 5.5616, "longitude": -0.1987},
        "Kasoa General": {"latitude": 5.5350, "longitude": -0.4350}
    }

    # Prepare data for map (only the selected hospital)
    selected_hospital_name = hospital
    selected_coords = hospital_coords.get(selected_hospital_name)

    if selected_coords:
        map_data = pd.DataFrame([
            {
                'latitude': selected_coords['latitude'],
                'longitude': selected_coords['longitude'],
                'name': selected_hospital_name
            }
        ])

        # Assign color based on probability and display status message
        if prob > 0.6:
            st.success("✅ High probability of bed availability.")
            map_data['color'] = [[0, 255, 0, 160]] # Green (RGBA)
        elif prob > 0.3:
            st.warning("⚠️ Limited capacity. Monitor closely.")
            map_data['color'] = [[255, 255, 0, 160]] # Yellow (RGBA)
        else:
            st.error("🚨 CRITICAL: No beds predicted. Initiate rerouting protocol.")
            map_data['color'] = [[255, 0, 0, 160]] # Red (RGBA)

        st.markdown("### Smart Route (Real-time GIS)")

        # Create a PyDeck layer for the scatterplot
        layer = pdk.Layer(
            "ScatterplotLayer",
            map_data,
            get_position='[longitude, latitude]',
            get_color='color',
            get_radius=200, # Radius in meters
            pickable=True,
            tooltip={
                "html": "<b>Hospital:</b> {name}<br>",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
        )

        # Set the initial view state for the map
        view_state = pdk.ViewState(
            latitude=selected_coords['latitude'],
            longitude=selected_coords['longitude'],
            zoom=12,
            pitch=50,
        )

        # Create a PyDeck object and display it
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9", # Light map style
            initial_view_state=view_state,
            layers=[layer],
        ))

    else:
        st.error(f"Coordinates not found for {selected_hospital_name}")


    # Display Security Audit for verification
    with st.expander("🛡️ Security Framework Audit Log"):
        st.json(audit_log)


except Exception as e:
    st.error(f"Application Error: {str(e)}")
