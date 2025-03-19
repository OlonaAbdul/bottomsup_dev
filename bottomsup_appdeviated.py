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

# Store live pump speed persistently
if "live_pump_speed" not in st.session_state:
    st.session_state.live_pump_speed = pump_speed

st.session_state.live_pump_speed = st.number_input(
    "Live Pump Speed (spm)", min_value=0.0, step=0.1, value=st.session_state.live_pump_speed, key="live_pump_speed"
)

if st.button("Start Tracking Sample"):
    current_depth = current_hole_depth
    sample_reached_surface = False
    depth_display = st.empty()  # To prevent multiple print lines

    while current_depth > 0 and not sample_reached_surface:
                live_pump_output = st.session_state.live_pump_speed * pump_rating
        
        if live_pump_output > 0:
            # Recalculate lag time dynamically
            updated_lag_time = total_annular_volume / live_pump_output
            upward_velocity = live_pump_output / annular_area  # ft/min
            depth_change_per_second = upward_velocity / 60  # Convert to feet per second
            
            # Update UI for lag time
            lag_time_display.write(f"**Updated Lag Time:** {updated_lag_time:.2f} minutes")

            time.sleep(45)  # Update every 45 seconds
            current_depth = max(0, current_depth - (depth_change_per_second * 45))
            depth_display.write(f"**Current Sample Depth:** {current_depth:.2f} ft")
        else:
            st.warning("Pump output is zero. Sample is not moving!")
            break

        
        if current_depth == 0:
            depth_display.success("✅ Sample has reached the surface!")
            sample_reached_surface = True
