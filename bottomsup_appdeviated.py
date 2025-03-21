import streamlit as st
import time
import datetime

# Initialize session state for samples if not already set
if 'samples' not in st.session_state:
    st.session_state.samples = {}

# Function to update countdowns
def update_countdowns():
    current_time = time.time()
    for sample in list(st.session_state.samples.keys()):
        data = st.session_state.samples[sample]
        if 'start_time' in data and data['status'] == "Running":
            elapsed = current_time - data['start_time']
            remaining = max(0, data['lag_time'] - int(elapsed))
            data['remaining_time'] = remaining
            if remaining == 0:
                data['status'] = "Completed"
    st.rerun()

# Title and Description
st.title("Lag Time Calculator and Tracker")
st.write("Calculate and track multiple lag time calculations in parallel.")

# Sidebar for Sample List
st.sidebar.header("Active Samples")
for sample, data in st.session_state.samples.items():
    time_display = str(datetime.timedelta(seconds=data.get('remaining_time', 0)))
    st.sidebar.write(f"{sample}: {time_display} ({data['status']})")
    
# Input Form for Calculator
st.header("Lag Time Calculator")

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
last_casing_depth = last_casing_shoe_depth - length_surface
length_open_hole = max(0, current_hole_depth - (last_casing_depth + length_surface))
length_drill_collar_in_casing = max(0, end_of_drill_collar - length_open_hole)
length_drill_collar_in_open_hole = end_of_drill_collar - length_drill_collar_in_casing
length_drill_pipe_in_casing = last_casing_depth - length_drill_collar_in_casing
length_drill_pipe_in_open_hole = max(0, length_open_hole - end_of_drill_collar)

# Annular Volume Calculations
av_open_hole = ((diameter_open_hole**2 - ext_diameter_drill_collar**2) * 0.000971 * length_drill_collar_in_open_hole) +                ((diameter_open_hole**2 - ext_diameter_hwdp**2) * 0.000971 * length_drill_pipe_in_open_hole)
av_cased_hole = ((int_diameter_casing**2 - ext_diameter_drill_collar**2) * 0.000971 * length_drill_collar_in_casing) +                 ((int_diameter_casing**2 - ext_diameter_hwdp**2) * 0.000971 * length_drill_pipe_in_casing)
av_surface = ((int_diameter_riser**2 - ext_diameter_hwdp**2) * 0.000971 * length_surface)

# Pump Output and Lag Time Calculation
pump_speed = st.number_input("Pump Speed (spm)", min_value=0.1, step=0.1)
pump_rating = st.number_input("Pump Rating (bbl/stroke)", min_value=0.01, step=0.01)

pump_output = pump_speed * pump_rating
st.write(f"Pump Output: {pump_output:.2f} bbls/min")

if pump_output > 0:
    lag_time = (av_open_hole + av_cased_hole + av_surface) / pump_output
    lag_time_seconds = int(lag_time * 60)  # Convert minutes to seconds
    st.success(f"Lag Time: {lag_time:.2f} minutes ({lag_time_seconds} seconds)")
else:
    st.warning("Pump output must be greater than 0 to calculate lag time.")
    lag_time_seconds = None

# Start Tracking Multiple Samples
st.header("Start a New Sample Tracking")
sample_name = st.text_input("Sample Name (e.g., Sample_3000ft)")

if lag_time_seconds and st.button("Start Tracking"):
    if sample_name and sample_name not in st.session_state.samples:
        st.session_state.samples[sample_name] = {
            'lag_time': lag_time_seconds,
            'remaining_time': lag_time_seconds,
            'status': "Running",
            'start_time': time.time()
        }
    elif sample_name in st.session_state.samples:
        st.warning("Sample name must be unique!")
    else:
        st.warning("Please provide a sample name.")

# Auto-update countdown
if len(st.session_state.samples) > 0:
    time.sleep(1)
    update_countdowns()
