import streamlit as st
import time

# Title and Description
st.title("Lag Time Calculator with Real-Time Tracking")
st.write("""
This application calculates **Bottoms-Up Time** based on well geometry and operational parameters.
Now featuring **real-time tracking** for sample movement!
""")

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

# Annular Volume Calculations (bbls)
av_open_hole = ((diameter_open_hole**2 - ext_diameter_drill_collar**2) * 0.000971 * length_drill_collar_in_open_hole) + \
               ((diameter_open_hole**2 - ext_diameter_hwdp**2) * 0.000971 * length_drill_pipe_in_open_hole)
av_cased_hole = ((int_diameter_casing**2 - ext_diameter_drill_collar**2) * 0.000971 * length_drill_collar_in_casing) + \
                ((int_diameter_casing**2 - ext_diameter_hwdp**2) * 0.000971 * length_drill_pipe_in_casing)
av_surface = ((int_diameter_riser**2 - ext_diameter_hwdp**2) * 0.000971 * length_surface)

total_annular_volume = av_open_hole + av_cased_hole + av_surface

# Pump Output and Lag Time
st.header("Pump Output and Lag Time")
pump_speed = st.number_input("Initial Pump Speed (spm)", min_value=0.0, step=0.1)
pump_rating = st.number_input("Pump Rating (bbl/stroke)", min_value=0.0, step=0.01)

pump_output = pump_speed * pump_rating  # bbl/min

if pump_output > 0:
    lag_time = total_annular_volume / pump_output
    annular_area = total_annular_volume / current_hole_depth  # bbl/ft
    upward_velocity = pump_output / annular_area  # ft/min
    st.success(f"Lag Time: {lag_time:.2f} minutes")
else:
    st.warning("Pump output must be greater than 0 to calculate lag time.")

# Real-Time Tracking
st.header("Real-Time Sample Tracking")

# Initialize session state for tracking
if "tracking" not in st.session_state:
    st.session_state.tracking = False
    st.session_state.current_depth = current_hole_depth
    st.session_state.live_pump_speed = pump_speed

# Ensure new_pump_speed is initialized before usage
if "new_pump_speed" not in st.session_state:
    st.session_state.new_pump_speed = st.session_state.live_pump_speed

def update_live_pump_speed():
    st.session_state.live_pump_speed = st.session_state.new_pump_speed
    st.rerun()  # Ensures UI updates

# Use number_input without direct assignment to session_state
st.number_input(
    "Live Pump Speed (spm)", 
    min_value=0.0, 
    step=0.1, 
    value=st.session_state.new_pump_speed, 
    key="new_pump_speed", 
    on_change=update_live_pump_speed
)

depth_display = st.empty()
lag_time_display = st.empty()

# Start/Stop Tracking Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Tracking Sample"):
        st.session_state.tracking = True
with col2:
    if st.button("Stop Tracking"):
        st.session_state.tracking = False

# Update tracking progress only if tracking is active
if st.session_state.tracking and st.session_state.current_depth > 0:
    live_pump_output = st.session_state.live_pump_speed * pump_rating

    if live_pump_output > 0:
        # Recalculate lag time dynamically
        updated_lag_time = total_annular_volume / live_pump_output
        upward_velocity = live_pump_output / annular_area  # ft/min
        depth_change_per_second = upward_velocity / 60  # Convert to feet per second

        # Update depth every 5 seconds
        st.session_state.current_depth = max(0, st.session_state.current_depth - (depth_change_per_second * 5))

        # Display updates
        lag_time_display.write(f"**Updated Lag Time:** {updated_lag_time:.2f} minutes")
        depth_display.write(f"**Current Sample Depth:** {st.session_state.current_depth:.2f} ft")

        if st.session_state.current_depth == 0:
            depth_display.success("✅ Sample has reached the surface!")
            st.session_state.tracking = False

        # Rerun the app every 5 seconds
        time.sleep(5)
        st.rerun()

    else:
        st.warning("Pump output is zero. Sample is not moving!")
        st.session_state.tracking = False
