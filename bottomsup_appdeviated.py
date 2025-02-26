
import streamlit as st
import math

# Title and Description
st.title("Lag Time Calculator for Mudlogging")
st.write("""
This application calculates **Bottoms-Up Time** based on well geometry, operational parameters, slippage factor, and flowline corrections.
""")

# Input Section
st.header("Input Parameters")

# User Inputs for Diameters (in inches)
ext_diameter_hwdp = st.number_input("External Diameter of HWDP/Drill Pipe (in)", min_value=0.0, step=0.1)
ext_diameter_drill_collar = st.number_input("External Diameter of Drill Collar (in)", min_value=0.0, step=0.1)
int_diameter_riser = st.number_input("Internal Diameter of Riser (in)", min_value=0.0, step=0.1)
int_diameter_casing = st.number_input("Internal Diameter of Casing (in)", min_value=0.0, step=0.1)
diameter_open_hole = st.number_input("Diameter of Open Hole (in)", min_value=0.0, step=0.1)
int_diameter_flowline = st.number_input("Internal Diameter of Flowline (in)", min_value=0.0, step=0.1)

# User Inputs for Lengths (in feet)
current_measured_depth = st.number_input("Current Measured Depth (MD) from Field Data (ft)", min_value=0.0, step=1.0)
last_casing_shoe_depth = st.number_input("Last Casing Shoe Depth (ft)", min_value=0.0, step=1.0)
end_of_drill_collar = st.number_input("End of Drill Collar (ft)", min_value=0.0, step=1.0)
length_surface = st.number_input("Length of Surface (ft)", min_value=0.0, step=1.0)
length_flowline = st.number_input("Length of Flowline (ft)", min_value=0.0, step=1.0)

# Mud Type Selection and Automatic Slippage Factor Assignment
mud_type = st.selectbox("Select Mud Type", [
    "Air Drilling (0.3 - 0.5)", "Aerated Mud (0.5 - 0.7)", "Low-Density Water-Based Mud (<9.5 ppg, 0.6 - 0.75)",
    "High-Density Water-Based Mud (>12 ppg, 0.75 - 0.9)", "Low-Density Oil-Based Mud (<12 ppg, 0.8 - 0.9)",
    "High-Density Oil-Based Mud (>14 ppg, 0.9 - 0.98)", "Synthetic-Based Mud (0.85 - 0.98)", "Weighted OBM/WBM (>16 ppg, 0.95 - 1.0)"
])

slippage_factors = {
    "Air Drilling (0.3 - 0.5)": 0.4, "Aerated Mud (0.5 - 0.7)": 0.6, "Low-Density Water-Based Mud (<9.5 ppg, 0.6 - 0.75)": 0.675,
    "High-Density Water-Based Mud (>12 ppg, 0.75 - 0.9)": 0.825, "Low-Density Oil-Based Mud (<12 ppg, 0.8 - 0.9)": 0.85,
    "High-Density Oil-Based Mud (>14 ppg, 0.9 - 0.98)": 0.94, "Synthetic-Based Mud (0.85 - 0.98)": 0.915, "Weighted OBM/WBM (>16 ppg, 0.95 - 1.0)": 0.975
}

slippage_factor = slippage_factors[mud_type]
st.write(f"Automatically Assigned Slippage Factor: {slippage_factor:.2f}")

if slippage_factor >= 0.9:
    st.info("Minimal slippage: High efficiency.")
elif 0.75 <= slippage_factor < 0.9:
    st.info("Moderate slippage: Balanced efficiency.")
else:
    st.warning("High slippage: Significant inefficiencies.")


# Derived Lengths
st.header("Derived Parameters")
last_casing_depth = last_casing_shoe_depth - length_surface
st.write(f"Last Casing Depth: {last_casing_depth:.2f} ft")

length_open_hole = max(0, current_measured_depth - (last_casing_depth + length_surface))
st.write(f"Length of Open Hole from Casing Shoe: {length_open_hole:.2f} ft")

length_drill_collar_in_casing = max(0, end_of_drill_collar - length_open_hole)
st.write(f"Length of Drill Collar in Casing: {length_drill_collar_in_casing:.2f} ft")

length_drill_collar_in_open_hole = max(0, end_of_drill_collar - length_drill_collar_in_casing)
st.write(f"Length of Drill Collar in Open Hole: {length_drill_collar_in_open_hole:.2f} ft")

length_drill_pipe_in_casing = max(0, last_casing_depth - length_drill_collar_in_casing)
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

av_flowline = (int_diameter_flowline**2 * 0.000971 * length_flowline)
st.write(f"Annular Volume of Flowline to Shale Shakers: {av_flowline:.2f} bbls")

# Total Annular Volume (including flowline)
av_total_corrected = av_open_hole + av_cased_hole + av_surface + av_flowline
st.write(f"Total Corrected Annular Volume: {av_total_corrected:.2f} bbls")

# Pump Output and Lag Time
st.header("Pump Output and Lag Time")
pump_speed = st.number_input("Pump Speed (spm)", min_value=0.0, step=0.1)
pump_rating = st.number_input("Pump Rating (bbl/stroke)", min_value=0.0, step=0.01)

pump_output = pump_speed * pump_rating
st.write(f"Pump Output: {pump_output:.2f} bbls/min")

if pump_output > 0:
    effective_pump_output = pump_output * slippage_factor
    lag_time_corrected = av_total_corrected / effective_pump_output
    st.success(f"Corrected Lag Time: {lag_time_corrected:.2f} minutes")
else:
    st.warning("Pump output must be greater than 0 to calculate lag time.")
