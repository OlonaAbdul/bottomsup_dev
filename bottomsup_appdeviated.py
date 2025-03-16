import streamlit as st
import pandas as pd
import time

# Initialize session state for tracking updates
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=['Timestamp', 'Pump Speed (spm)', 'Pump Output (bbl/min)', 'Remaining Depth (ft)', 'Estimated Time to Surface (min)'])
if 'traveling' not in st.session_state:
    st.session_state['traveling'] = False

# Title and Description
st.title("Lag Time Calculator for Mudlogging")
st.write("""
This application calculates **Bottoms-Up Time** based on well geometry and operational parameters. Provide the required inputs below.
""")

# Input Section
st.header("Input Parameters")

# User Inputs for Diameters (in inches)
ext_diameter_hwdp = st.number_input("External Diameter of HWDP/Drill Pipe (in)", min_value=0.0, step=0.1)
ext_diameter_drill_collar = st.number_input("External Diameter of Drill Collar (in)", min_value=0.0, step=0.1)
int_diameter_riser = st.number_input("Internal Diameter of Riser (in)", min_value=0.0, step=0.1)
int_diameter_casing = st.number_input("Internal Diameter of Casing (in)", min_value=0.0, step=0.1)
diameter_open_hole = st.number_input("Diameter of Open Hole (in)", min_value=0.0, step=0.1)

# User Inputs for Lengths (in feet)
last_casing_shoe_depth = st.number_input("Last Casing Shoe Depth (ft)", min_value=0.0, step=1.0)
current_hole_depth = st.number_input("Current Hole Depth (ft)", min_value=0.0, step=1.0)
end_of_drill_collar = st.number_input("End of Drill Collar (ft)", min_value=0.0, step=1.0)
length_surface = st.number_input("Length of Surface (ft)", min_value=0.0, step=1.0)

# Derived Lengths
st.header("Derived Parameters")
last_casing_depth = last_casing_shoe_depth - length_surface
st.write(f"Last Casing Depth: {last_casing_depth:.2f} ft")

length_open_hole = max(0, current_hole_depth - (last_casing_depth + length_surface))
st.write(f"Length of Open Hole from Casing Shoe: {length_open_hole:.2f} ft")

length_drill_collar_in_casing = max(0, end_of_drill_collar - length_open_hole)
st.write(f"Length of Drill Collar in Casing: {length_drill_collar_in_casing:.2f} ft")

length_drill_collar_in_open_hole = end_of_drill_collar - length_drill_collar_in_casing
st.write(f"Length of Drill Collar in Open Hole: {length_drill_collar_in_open_hole:.2f} ft")

length_drill_pipe_in_casing = last_casing_depth - length_drill_collar_in_casing
st.write(f"Length of Drill Pipe in Casing: {length_drill_pipe_in_casing:.2f} ft")

length_drill_pipe_in_open_hole = max(0, length_open_hole - end_of_drill_collar)
st.write(f"Length of Drill Pipe in Open Hole: {length_drill_pipe_in_open_hole:.2f} ft")

# Annular Volume Calculations
st.header("Annular Volumes (bbls)")

av_open_hole = ((diameter_open_hole**2 - ext_diameter_drill_collar**2) * 0.000971 * length_drill_collar_in_open_hole) +                ((diameter_open_hole**2 - ext_diameter_hwdp**2) * 0.000971 * length_drill_pipe_in_open_hole)
st.write(f"Annular Volume of Open Hole: {av_open_hole:.2f} bbls")

av_cased_hole = ((int_diameter_casing**2 - ext_diameter_drill_collar**2) * 0.000971 * length_drill_collar_in_casing) +                 ((int_diameter_casing**2 - ext_diameter_hwdp**2) * 0.000971 * length_drill_pipe_in_casing)
st.write(f"Annular Volume of Cased Hole: {av_cased_hole:.2f} bbls")

av_surface = ((int_diameter_riser**2 - ext_diameter_hwdp**2) * 0.000971 * length_surface)
st.write(f"Annular Volume of Surface Wellhead & Riser: {av_surface:.2f} bbls")

total_annular_volume = av_open_hole + av_cased_hole + av_surface

# Pump Output and Lag Time
st.header("Pump Output and Lag Time")
pump_speed = st.number_input("Pump Speed (spm)", min_value=0.0, step=0.1)
pump_rating = st.number_input("Pump Rating (bbl/stroke)", min_value=0.0, step=0.01)

pump_output = pump_speed * pump_rating
st.write(f"Pump Output: {pump_output:.2f} bbls/min")

if pump_output > 0:
    lag_time = total_annular_volume / pump_output
    st.success(f"Lag Time: {lag_time:.2f} minutes")
else:
    st.warning("Pump output must be greater than 0 to calculate lag time.")

# Real-Time Tracking Integration
st.header("Real-Time Lag Time Tracking")

depth_start = current_hole_depth  # Set tracking depth
if st.button("Start Tracking"):
    st.session_state['traveling'] = True
    st.session_state['remaining_depth'] = depth_start

if st.session_state['traveling']:
    remaining_depth = st.session_state['remaining_depth']
    while remaining_depth > 0:
        if pump_output > 0:
            estimated_time = total_annular_volume / pump_output
        else:
            estimated_time = float('inf')
        
        st.metric(label="Time to Surface (min)", value=f"{estimated_time:.2f}")
        progress = 1 - (st.session_state['remaining_depth'] / depth_start)
        st.progress(min(progress, 1.0))
        
        if st.session_state['remaining_depth'] <= 0:
            st.success("Sample has reached the surface!")
            st.balloons()
            st.session_state['traveling'] = False
        
        time.sleep(1)
        st.rerun()

st.header("Tracking History")
st.dataframe(st.session_state['data'])
