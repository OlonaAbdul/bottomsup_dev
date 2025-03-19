import streamlit as st
import time

# Title and Description
st.title("Lag Time Calculator with Real-Time Tracking")
st.write("""
This application calculates **Bottoms-Up Time** based on well geometry and operational parameters.
Now featuring **real-time tracking** for sample movement!
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
last_casing_depth = last_casing_shoe_depth - length_surface
length_open_hole = max(0, current_hole_depth - (last_casing_depth + length_surface))
length_drill_collar_in_casing = max(0, end_of_drill_collar - length_open_hole)
length_drill_collar_in_open_hole = end_of_drill_collar - length_drill_collar_in_casing
length_drill_pipe_in_casing = last_casing_depth - length_drill_collar_in_casing
length_drill_pipe_in_open_hole = max(0, length_open_hole - end_of_drill_collar)

# Display Derived Lengths
st.header("Derived Lengths")
st.write(f"**Last Casing Depth:** {last_casing_depth:.2f} ft")
st.write(f"**Length of Open Hole:** {length_open_hole:.2f} ft")
st.write(f"**Drill Collar in Casing:** {length_drill_collar_in_casing:.2f} ft")
st.write(f"**Drill Collar in Open Hole:** {length_drill_collar_in_open_hole:.2f} ft")
st.write(f"**Drill Pipe in Casing:** {length_drill_pipe_in_casing:.2f} ft")
st.write(f"**Drill Pipe in Open Hole:** {length_drill_pipe_in_open_hole:.2f} ft")

# Annular Volume Calculations (bbls)
av_open_hole = ((diameter_open_hole**2 - ext_diameter_drill_collar**2) * 0.000971 * length_drill_collar_in_open_hole) + \
               ((diameter_open_hole**2 - ext_diameter_hwdp**2) * 0.000971 * length_drill_pipe_in_open_hole)
av_cased_hole = ((int_diameter_casing**2 - ext_diameter_drill_collar**2) * 0.000971 * length_drill_collar_in_casing) + \
                ((int_diameter_casing**2 - ext_diameter_hwdp**2) * 0.000971 * length_drill_pipe_in_casing)
av_surface = ((int_diameter_riser**2 - ext_diameter_hwdp**2) * 0.000971 * length_surface)

total_annular_volume = av_open_hole + av_cased_hole + av_surface

# Display Annular Volumes
st.header("Annular Volume Calculations")
st.write(f"**Annular Volume in Open Hole:** {av_open_hole:.2f} bbls")
st.write(f"**Annular Volume in Cased Hole:** {av_cased_hole:.2f} bbls")
st.write(f"**Annular Volume in Surface:** {av_surface:.2f} bbls")
st.write(f"**Total Annular Volume:** {total_annular_volume:.2f} bbls")

# Pump Output and Lag Time
st.header("Pump Output and Lag Time")
pump_speed = st.number_input("Initial Pump Speed (spm)", min_value=0.0, step=0.1)
pump_rating = st.number_input("Pump Rating (bbl/stroke)", min_value=0.0, step=0.01)

pump_output = pump_speed * pump_rating
if pump_output > 0:
    lag_time = total_annular_volume / pump_output
    st.success(f"Lag Time: {lag_time:.2f} minutes")
else:
    st.warning("Pump output must be greater than 0 to calculate lag time.")

# Real-Time Tracking Section
if st.button("Start Tracking Sample"):
    st.header("Real-Time Sample Tracking")
    live_pump_speed = st.number_input("Live Pump Speed (spm)", min_value=0.0, step=0.1, value=pump_speed, key="live_pump_speed")
    current_depth = current_hole_depth
    sample_reached_surface = False
    
    while current_depth > 0 and not sample_reached_surface:
        live_pump_output = live_pump_speed * pump_rating
        if live_pump_output > 0:
            upward_velocity = total_annular_volume / (lag_time * current_hole_depth)
            depth_change_per_second = upward_velocity / 60  # Convert to feet per second
            time.sleep(45)  # Update every 45 seconds
            current_depth = max(0, current_depth - (depth_change_per_second * 45))
            st.write(f"Current Sample Depth: {current_depth:.2f} ft")
        else:
            st.warning("Pump output is zero. Sample is not moving!")
            break
        
        if current_depth == 0:
            st.success("✅ Sample has reached the surface!")
            sample_reached_surface = True
