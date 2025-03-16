import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Initialize session state for tracking updates
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=[
        'Timestamp', 'Pump Speed (spm)', 'Pump Output (bbl/min)', 'Remaining Time (min)',
        'Ext Diameter HWDP (in)', 'Ext Diameter Drill Collar (in)', 'Int Diameter Riser (in)', 'Int Diameter Casing (in)', 'Diameter Open Hole (in)',
        'Last Casing Shoe Depth (ft)', 'Current Hole Depth (ft)', 'End of Drill Collar (ft)', 'Length Surface (ft)',
        'Annular Volume Open Hole (bbls)', 'Annular Volume Cased Hole (bbls)', 'Annular Volume Surface (bbls)', 'Total Annular Volume (bbls)', 'Lag Time (min)'
    ])
if 'countdown_start' not in st.session_state:
    st.session_state['countdown_start'] = None
if 'remaining_time' not in st.session_state:
    st.session_state['remaining_time'] = None
if 'tracking' not in st.session_state:
    st.session_state['tracking'] = False
if 'last_pump_speed' not in st.session_state:
    st.session_state['last_pump_speed'] = None

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
av_open_hole = ((diameter_open_hole**2 - ext_diameter_drill_collar**2) * 0.000971 * length_open_hole)
st.write(f"Annular Volume of Open Hole: {av_open_hole:.2f} bbls")

av_cased_hole = ((int_diameter_casing**2 - ext_diameter_drill_collar**2) * 0.000971 * last_casing_depth)
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
    if st.session_state['tracking']:
        elapsed_time = (time.time() - st.session_state['countdown_start']) / 60
        st.session_state['remaining_time'] = max(0, lag_time - elapsed_time)
else:
    lag_time = float('inf')
st.success(f"Lag Time: {lag_time:.2f} minutes")

if st.button("Start Countdown"):
    st.session_state['countdown_start'] = time.time()
    st.session_state['remaining_time'] = lag_time
    st.session_state['tracking'] = True
    st.session_state['last_pump_speed'] = pump_speed

countdown_placeholder = st.empty()

def update_data():
    while st.session_state['tracking'] and st.session_state['remaining_time'] > 0:
        elapsed_time = (time.time() - st.session_state['countdown_start']) / 60
        st.session_state['remaining_time'] = max(0, lag_time - elapsed_time)
        if pump_speed != st.session_state['last_pump_speed']:
            st.session_state['countdown_start'] = time.time()
            lag_time = total_annular_volume / pump_output
            st.session_state['last_pump_speed'] = pump_speed
        new_data = pd.DataFrame({
            'Timestamp': [datetime.now()],
            'Pump Speed (spm)': [pump_speed],
            'Pump Output (bbl/min)': [pump_output],
            'Remaining Time (min)': [st.session_state['remaining_time']],
            'Total Annular Volume (bbls)': [total_annular_volume],
            'Lag Time (min)': [lag_time]
        })
        st.session_state['data'] = pd.concat([st.session_state['data'], new_data], ignore_index=True)
        countdown_placeholder.warning(f"Sample will reach surface in {st.session_state['remaining_time']:.2f} minutes")
        time.sleep(1)
    countdown_placeholder.success("Sample has reached the surface!")
    st.balloons()

if st.session_state['tracking']:
    update_data()

st.dataframe(st.session_state['data'])
