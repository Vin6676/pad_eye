import streamlit as st
import math
from PIL import Image, ImageDraw, ImageFont
import io

# Constants for calculations
F_BY_FACTOR = 0.9   # Bearing stress factor
F_V_FACTOR = 0.4    # Pull-out shear stress factor
F_T_FACTOR = 0.45   # Tear-out stress factor
F_TE_FACTOR = 0.6   # Tensile stress factor
ALLOWABLE_WELD_STRESS = 0.3 * 70 * 6.895  # Approximately 144.8 MPa

shackle_data = {
    # G213 series (15 entries)
    "G213 - 1/2T":   {"SWL": 0.50,  "Jaw Width": 11.9,   "Pin Diameter": 7.9,   "Inside Length": 28.7},
    "G213 - 3/4T":   {"SWL": 0.75,  "Jaw Width": 13.5,   "Pin Diameter": 9.7,   "Inside Length": 31.0},
    "G213 - 1T":     {"SWL": 1,     "Jaw Width": 16.8,   "Pin Diameter": 11.2,  "Inside Length": 36.6},
    "G213 - 1-1/2T": {"SWL": 1.50,  "Jaw Width": 19.1,   "Pin Diameter": 12.7,  "Inside Length": 42.9},
    "G213 - 2T":     {"SWL": 2,     "Jaw Width": 20.6,   "Pin Diameter": 16,    "Inside Length": 47.8},
    "G213 - 3-1/4T": {"SWL": 3.25,  "Jaw Width": 26.9,   "Pin Diameter": 19.1,  "Inside Length": 60.5},
    "G213 - 4-3/4T": {"SWL": 4.75,  "Jaw Width": 31.8,   "Pin Diameter": 22.4,  "Inside Length": 71.5},
    "G213 - 6-1/2T": {"SWL": 6.50,  "Jaw Width": 36.6,   "Pin Diameter": 25.4,  "Inside Length": 84},
    "G213 - 8-1/2T": {"SWL": 8.50,  "Jaw Width": 42.9,   "Pin Diameter": 28.7,  "Inside Length": 95.5},
    "G213 - 9-1/2T": {"SWL": 9.50,  "Jaw Width": 46.0,   "Pin Diameter": 31.8,  "Inside Length": 108},
    "G213 - 12T":    {"SWL": 12,    "Jaw Width": 51.5,   "Pin Diameter": 35.1,  "Inside Length": 119},
    "G213 - 13-1/2T":{"SWL": 13.50, "Jaw Width": 57,     "Pin Diameter": 38.1,  "Inside Length": 133},
    "G213 - 17T":    {"SWL": 17,    "Jaw Width": 60.5,   "Pin Diameter": 41.4,  "Inside Length": 146},
    "G213 - 25T":    {"SWL": 25,    "Jaw Width": 73,     "Pin Diameter": 51,    "Inside Length": 178},
    "G213 - 35T":    {"SWL": 35,    "Jaw Width": 82.5,   "Pin Diameter": 57,    "Inside Length": 197},

    # G209 series (17 entries)
    "G209 - 1/3T":   {"SWL": 0.33,  "Jaw Width": 9.65,   "Pin Diameter": 6.35,  "Inside Length": 22.4},
    "G209 - 1/2T":   {"SWL": 0.50,  "Jaw Width": 11.9,   "Pin Diameter": 7.85,  "Inside Length": 28.7},
    "G209 - 3/4T":   {"SWL": 0.75,  "Jaw Width": 13.5,   "Pin Diameter": 9.65,  "Inside Length": 31},
    "G209 - 1T":     {"SWL": 1,     "Jaw Width": 16.8,   "Pin Diameter": 11.2,  "Inside Length": 36.6},
    "G209 - 1-1/2T": {"SWL": 1.50,  "Jaw Width": 19.1,   "Pin Diameter": 12.7,  "Inside Length": 42.9},
    "G209 - 2T":     {"SWL": 2,     "Jaw Width": 20.6,   "Pin Diameter": 16,    "Inside Length": 47.8},
    "G209 - 3-1/4T": {"SWL": 3.25,  "Jaw Width": 26.9,   "Pin Diameter": 19.1,  "Inside Length": 60.5},
    "G209 - 4-3/4T": {"SWL": 4.75,  "Jaw Width": 31.8,   "Pin Diameter": 22.4,  "Inside Length": 71.5},
    "G209 - 6-1/2T": {"SWL": 6.50,  "Jaw Width": 36.6,   "Pin Diameter": 25.4,  "Inside Length": 84},
    "G209 - 8-1/2T": {"SWL": 8.50,  "Jaw Width": 42.9,   "Pin Diameter": 28.7,  "Inside Length": 95.5},
    "G209 - 9-1/2T": {"SWL": 9.50,  "Jaw Width": 46.0,   "Pin Diameter": 31.8,  "Inside Length": 108},
    "G209 - 12T":    {"SWL": 12,    "Jaw Width": 51.5,   "Pin Diameter": 35.1,  "Inside Length": 119},
    "G209 - 13-1/2T":{"SWL": 13.50, "Jaw Width": 57,     "Pin Diameter": 38.1,  "Inside Length": 133},
    "G209 - 17T":    {"SWL": 17,    "Jaw Width": 60.5,   "Pin Diameter": 41.4,  "Inside Length": 146},
    "G209 - 25T":    {"SWL": 25,    "Jaw Width": 73,     "Pin Diameter": 51,    "Inside Length": 178},
    "G209 - 35T":    {"SWL": 35,    "Jaw Width": 82.5,   "Pin Diameter": 57,    "Inside Length": 197},
    "G209 - 55T":    {"SWL": 55,    "Jaw Width": 105,    "Pin Diameter": 70,    "Inside Length": 267},

    # G2130 series (20 entries)
    "G2130 - 1/3T":   {"SWL": 0.33,  "Jaw Width": 9.65,  "Pin Diameter": 6.35,  "Inside Length": 22.4},
    "G2130 - 1/2T":   {"SWL": 0.50,  "Jaw Width": 11.9,  "Pin Diameter": 7.85,  "Inside Length": 28.7},
    "G2130 - 3/4T":   {"SWL": 0.75,  "Jaw Width": 13.5,  "Pin Diameter": 9.65,  "Inside Length": 31},
    "G2130 - 1T":     {"SWL": 1,     "Jaw Width": 16.8,  "Pin Diameter": 11.2,  "Inside Length": 36.6},
    "G2130 - 1-1/2T": {"SWL": 1.50,  "Jaw Width": 19.1,  "Pin Diameter": 12.7,  "Inside Length": 42.9},
    "G2130 - 2T":     {"SWL": 2,     "Jaw Width": 20.6,  "Pin Diameter": 16,    "Inside Length": 47.8},
    "G2130 - 3-1/4T": {"SWL": 3.25,  "Jaw Width": 26.9,  "Pin Diameter": 19.1,  "Inside Length": 60.5},
    "G2130 - 4-3/4T": {"SWL": 4.75,  "Jaw Width": 31.8,  "Pin Diameter": 22.4,  "Inside Length": 71.5},
    "G2130 - 6-1/2T": {"SWL": 6.50,  "Jaw Width": 36.6,  "Pin Diameter": 25.4,  "Inside Length": 84},
    "G2130 - 8-1/2T": {"SWL": 8.50,  "Jaw Width": 42.9,  "Pin Diameter": 28.7,  "Inside Length": 95.5},
    "G2130 - 9-1/2T": {"SWL": 9.50,  "Jaw Width": 46,    "Pin Diameter": 31.8,  "Inside Length": 108},
    "G2130 - 12T":    {"SWL": 12,    "Jaw Width": 51.5,  "Pin Diameter": 35.1,  "Inside Length": 119},
    "G2130 - 13-1/2T":{"SWL": 13.50, "Jaw Width": 57,    "Pin Diameter": 38.1,  "Inside Length": 133},
    "G2130 - 17T":    {"SWL": 17,    "Jaw Width": 60.5,  "Pin Diameter": 41.4,  "Inside Length": 146},
    "G2130 - 25T":    {"SWL": 25,    "Jaw Width": 73,    "Pin Diameter": 51,    "Inside Length": 178},
    "G2130 - 35T":    {"SWL": 35,    "Jaw Width": 82.5,  "Pin Diameter": 57,    "Inside Length": 197},
    "G2130 - 55T":    {"SWL": 55,    "Jaw Width": 105,   "Pin Diameter": 70,    "Inside Length": 267},
    "G2130 - 85T":    {"SWL": 85,    "Jaw Width": 127,   "Pin Diameter": 82.5,  "Inside Length": 330},
    "G2130 - 120T":   {"SWL": 120,   "Jaw Width": 133,   "Pin Diameter": 95.5,  "Inside Length": 372},
    "G2130 - 150T":   {"SWL": 150,   "Jaw Width": 140,   "Pin Diameter": 108,   "Inside Length": 368},

    # G2140 series (21 entries)
    "G2140 - 2T":      {"SWL": 2,     "Jaw Width": 16.8,  "Pin Diameter": 11.2,  "Inside Length": 36.6},
    "G2140 - 2.67T":   {"SWL": 2.67,  "Jaw Width": 19.1,  "Pin Diameter": 12.7,  "Inside Length": 42.9},
    "G2140 - 3.33T":   {"SWL": 3.33,  "Jaw Width": 20.6,  "Pin Diameter": 16.3,  "Inside Length": 47.8},
    "G2140 - 5T":      {"SWL": 5,     "Jaw Width": 26.9,  "Pin Diameter": 19.6,  "Inside Length": 60.5},
    "G2140 - 7T":      {"SWL": 7,     "Jaw Width": 31.8,  "Pin Diameter": 22.6,  "Inside Length": 71.4},
    "G2140 - 9.5T":    {"SWL": 9.5,   "Jaw Width": 36.6,  "Pin Diameter": 25.9,  "Inside Length": 84.1},
    "G2140 - 12.5T":   {"SWL": 12.5,  "Jaw Width": 42.9,  "Pin Diameter": 29.2,  "Inside Length": 95.3},
    "G2140 - 15T":     {"SWL": 15,    "Jaw Width": 46,    "Pin Diameter": 31.8,  "Inside Length": 108},
    "G2140 - 18T":     {"SWL": 18,    "Jaw Width": 51.6,  "Pin Diameter": 35.6,  "Inside Length": 119.1},
    "G2140 - 21T":     {"SWL": 21,    "Jaw Width": 57.2,  "Pin Diameter": 38.9,  "Inside Length": 133.4},
    "G2140 - 30T":     {"SWL": 30,    "Jaw Width": 60.5,  "Pin Diameter": 41.4,  "Inside Length": 146},
    "G2140 - 40T":     {"SWL": 40,    "Jaw Width": 73.2,  "Pin Diameter": 50.8,  "Inside Length": 178},
    "G2140 - 55T":     {"SWL": 55,    "Jaw Width": 82.6,  "Pin Diameter": 57.2,  "Inside Length": 197},
    "G2140 - 85T":     {"SWL": 85,    "Jaw Width": 105,   "Pin Diameter": 69.9,  "Inside Length": 267},
    "G2140 - 120T":    {"SWL": 120,   "Jaw Width": 127,   "Pin Diameter": 82.6,  "Inside Length": 330},
    "G2140 - 150T":    {"SWL": 150,   "Jaw Width": 133,   "Pin Diameter": 95.3,  "Inside Length": 372},
    "G2140 - 175T":    {"SWL": 175,   "Jaw Width": 140,   "Pin Diameter": 108,   "Inside Length": 368},
    "G2140 - 200T":    {"SWL": 200,   "Jaw Width": 184,   "Pin Diameter": 121,   "Inside Length": 386},
    "G2140 - 250T":    {"SWL": 250,   "Jaw Width": 216,   "Pin Diameter": 127,   "Inside Length": 470},
    "G2140 - 300T":    {"SWL": 300,   "Jaw Width": 213,   "Pin Diameter": 152,   "Inside Length": 475},
    "G2140 - 400T":    {"SWL": 400,   "Jaw Width": 210,   "Pin Diameter": 178,   "Inside Length": 572}
}

st.title("Pad-Eye Design & Shackle Selection Tool")
st.markdown("Enter all design parameters:")

# ---------------------------------------------------------
# 1: Loading Inputs
# ---------------------------------------------------------
st.header("1: Loading Inputs")
Ps    = st.number_input("Static sling load (Ps) in kN:", value=0.0, min_value=0.0, step=1.0, format="%.2f")
DAF   = st.number_input("Dynamic Amplification Factor, DAF (f):", value=0.0, min_value=0.0, step=0.1, format="%.2f")
theta = st.number_input("Loading angle with horizontal (θ) in degrees:", value=0.0, min_value=0.0, max_value=90.0, step=0.1, format="%.2f")
phi   = st.number_input("Sling's out-of-plane angle with pad-eye (φ) in degrees:", value=0.0, min_value=0.0, max_value=90.0, step=0.1, format="%.2f")
fop   = st.number_input("Additional out-of-plane load percentage (fop) in %:", value=0.0, min_value=0.0, step=0.1, format="%.2f")

# ---------------------------------------------------------
# 2: Shackle Details
# ---------------------------------------------------------
st.header("2: Shackle Details")
selected_shackle = st.selectbox("Select a Shackle Type:", list(shackle_data.keys()))

# Conversion factor: 1 metric ton (MT) = 10 kN 
conversion_factor = 10

# Get SWL in MT from the dictionary and convert to kN.
Psh_mt = shackle_data[selected_shackle]["SWL"]
Psh = Psh_mt * conversion_factor

# Use the other parameters directly
# [Previous code remains identical until the button click section]

# Use the other parameters directly from the dictionary (they are in mm)
B_val = shackle_data[selected_shackle]["Pin Diameter"]
A_val = shackle_data[selected_shackle]["Jaw Width"]
C_val = shackle_data[selected_shackle]["Inside Length"]

# Display the auto-filled values
st.write(f"**SWL of Shackle:** {Psh:.2f} kN")
st.write(f"**Pin Diameter (B):** {B_val:.2f} mm")
st.write(f"**Jaw Width (A):** {A_val:.2f} mm")
st.write(f"**Inside Length (C):** {C_val:.2f} mm")

# ---------------------------------------------------------
# 3: Rope/Sling Details
# ---------------------------------------------------------
st.header("3: Rope/Sling Details")
fr  = st.number_input("FOS against MBL of rope (fr):", value=0.0, min_value=0.0, step=0.1, format="%.2f")
MBL = st.number_input("MBL of rope required (MBL) in Kn:", value=0.0, min_value=0.0, step=0.1, format="%.2f")
dr  = st.number_input("Rope Diameter selected (dr) in mm:", value=0.0, min_value=0.0, step=0.1, format="%.2f")

# ---------------------------------------------------------
# 4: Pad-Eye Dimensions and Shackle Compatibility
# ---------------------------------------------------------
st.header("4: Pad-Eye Dimensions and Shackle Compatibility")
# --- Auto-calculate these values ---
dh = B_val + 1.5              # Pad-eye hole diameter
R = C_val + (dh / 2)          # Radius of main plate
r_val = R                     # Radius of cheek plate
T = round(0.75 * A_val, 2)    # Thickness of main plate
t_val = round((A_val - T)/2, 2) # Thickness of cheek plate
l_val = 2 * R                 # Base length of pad-eye
e_val = R                     # Eccentricity from base

# Display for user's awareness
st.subheader("Auto-Calculated Pad-Eye Dimensions")
st.write(f"Pad-eye Hole Diameter (dh): {dh:.2f} mm")
st.write(f"Radius of Main Plate (R): {R:.2f} mm")
st.write(f"Main Plate Thickness (T): {T:.2f} mm")
st.write(f"Cheek Plate Thickness (t): {t_val:.2f} mm")
st.write(f"Pad-eye Base Length (l): {l_val:.2f} mm")
st.write(f"Eccentricity (e): {e_val:.2f} mm")

fy   = st.number_input("Yield Strength of Pad-Eye Plate (fy) in MPa:", value=0.0, min_value=0.0, step=10.0, format="%.2f")
min_spread = st.number_input("Minimum Shackle Spread Percentage required (%):", value=0.0, min_value=0.0, step=0.1, format="%.2f")
twc  = st.number_input("Weld thickness between Cheek Plate and Pad-Eye Plate (twc) in mm:", value=0.0, min_value=0.0, step=0.1, format="%.2f")

# ---------------------------------------------------------
# Derived Geometry Calculations
# ---------------------------------------------------------
st.header("Derived Geometry Information")
min_inside_length_required = 1.5 * dr
actual_inside_length = C_val - (R - (dh / 2))
jaw_width_clearance = A_val - (T + 2*t_val)
actual_shackle_spread_pct = ((T + 2*t_val) / A_val) * 100 if A_val != 0 else 0

if st.button("Compute Derived Geometry & Design Checks"):
    st.subheader("Derived Geometry Calculations")
    st.write(f"Minimum Inside Length Clearance Required: {min_inside_length_required:.2f} mm")
    st.write(f"Actual Inside Length Clearance Provided: {actual_inside_length:.2f} mm")
    st.write(f"Jaw Width Clearance Provided: {jaw_width_clearance:.2f} mm")
    st.write(f"Actual Shackle Spread Percentage: {actual_shackle_spread_pct:.2f} %")
    
    # Safety check flags initialization
    safety_checks = {
        "Bearing": {"passed": True, "allowable": 0, "actual": 0},
        "Pull-Out Shear": {"passed": True, "allowable": 0, "actual": 0},
        "Tear Out": {"passed": True, "allowable": 0, "actual": 0},
        "Tensile": {"passed": True, "allowable": 0, "actual": 0},
        "Pad-Eye Base": {"passed": True, "allowable": 0, "actual": 0},
        "Weld": {"passed": True, "allowable": 0, "actual": 0}
    }

    # ---------------------------------------------------------
    # Section 2: Design Calculations
    # ---------------------------------------------------------
    st.header("DESIGN CALCULATIONS")
    rad_theta = math.radians(theta)
    rad_phi = math.radians(phi)
    P = Ps * DAF
    Pv = P * math.sin(rad_theta)
    Ph = P * math.cos(rad_theta) * math.cos(rad_phi)
    Po = P * math.cos(rad_theta) * math.sin(rad_phi) + (fop / 100.0) * P

    st.subheader("Computed Design Loads")
    st.write(f"Design Dynamic Load (P): {P:.2f} kN")
    st.write(f"In-plane Vertical Force (Pv): {Pv:.2f} kN")
    st.write(f"In-plane Horizontal Force (Ph): {Ph:.2f} kN")
    st.write(f"Out-of-plane Force (Po): {Po:.2f} kN")
    max_force = max(abs(Pv), abs(Ph), abs(Po))
    st.write(f"Maximum Applied Force Component: {max_force:.2f} kN")
    
    # 2.1 Bearing Check
    Ab = B_val * (T + 2*t_val)  # in mm²
    fby = F_BY_FACTOR * fy
    Pb_kN = (Ab * fby) / 1000.0

    # ✅ Actual load: bearing stress experienced = applied load / area
    actual_bearing_stress = Pv * 1000 / Ab  # N/mm²
    safety_checks["Bearing"]["actual"] = actual_bearing_stress  # in MPa
    safety_checks["Bearing"]["allowable"] = fby  # in MPa
    
    # 2.2 Pull-Out Shear Check
    Av = 2 * (((R - dh/2) * T) + (2 * (r_val - dh/2) * t_val))  # mm²
    fv = F_V_FACTOR * fy
    pullout_load_kN = Av * fv / 1000.0

    # ✅ Actual shear stress experienced
    actual_shear_stress = Ph * 1000 / Av
    safety_checks["Pull-Out Shear"]["actual"] = actual_shear_stress
    safety_checks["Pull-Out Shear"]["allowable"] = fv

    
    # 2.3 Tear Out Stress Check
    At = (2 * R - dh) * T + 2 * (2 * r_val - dh) * t_val  # mm²
    ft = F_T_FACTOR * fy
    tear_load_kN = At * ft / 1000.0

    # ✅ Actual tear stress experienced
    actual_tear_stress = Po * 1000 / At
    safety_checks["Tear Out"]["actual"] = actual_tear_stress
    safety_checks["Tear Out"]["allowable"] = ft

    
    # 2.4 Tensile Stress Check
    Ate = 2 * R * T  # mm²
    fte = F_TE_FACTOR * fy
    tensile_load_kN = Ate * fte / 1000.0

    # ✅ Actual tensile stress experienced
    actual_tensile_stress = max_force * 1000 / Ate
    safety_checks["Tensile"]["actual"] = actual_tensile_stress
    safety_checks["Tensile"]["allowable"] = fte

    
    # 2.6 Pad-Eye Base Check (Simplified Calculation)
    Aba = l_val * T
    I_ip = (T * (l_val**3)) / 12.0
    I_op = (l_val * (T**3)) / 12.0
    Zip = I_ip / (l_val/2.0) if l_val != 0 else float('inf')
    Zop = I_op / (T/2.0) if T != 0 else float('inf')
    
    fa = (Pv * 1000.0) / Aba
    fbip = (Ph * 1000.0 * e_val) / Zip if Zip != 0 else float('inf')
    fbop = (Po * 1000.0 * e_val) / Zop if Zop != 0 else float('inf')
    tau_ip = (Ph * 1000.0) / Aba
    tau_op = (Po * 1000.0) / Aba
    tau_combined = tau_ip + tau_op
    sigma_vm = math.sqrt(fa**2 + fbip**2 + fbop**2 + tau_combined**2)
    allowable_vm = 0.7 * fy
    safety_checks["Pad-Eye Base"]["passed"] = sigma_vm <= allowable_vm
    safety_checks["Pad-Eye Base"]["allowable"] = allowable_vm
    safety_checks["Pad-Eye Base"]["actual"] = sigma_vm
    
    # 2.7 Weld Check Between Pad-Eye and Cheek Plate
    if (T + 2*t_val) != 0:
        Pc = P * (t_val / (T + 2*t_val))
    else:
        Pc = 0
    if r_val > 0 and twc > 0:
        Awc = 0.5 * (2 * math.pi * r_val) * (0.707 * twc)
        tau_wc = (Pc * 1000.0) / Awc
        safety_checks["Weld"]["passed"] = tau_wc <= ALLOWABLE_WELD_STRESS
        safety_checks["Weld"]["allowable"] = ALLOWABLE_WELD_STRESS
        safety_checks["Weld"]["actual"] = tau_wc
    

# Header for safety check results
st.header("Safety Check Results")
col1, col2 = st.columns(2)

if "safety_checks" in locals():
    with col1:
        for check_name, values in safety_checks.items():
            # Weld check exclusion
            if check_name == "Weld" and (r_val <= 0 or twc <= 0):
                st.warning("Weld Check: Not applicable (r or twc ≤ 0)")
                continue

            status = "PASSED ✅" if values["passed"] else "FAILED ❌"
            units = "kN" if check_name in ["Bearing", "Pull-Out Shear", "Tear Out", "Tensile"] else "MPa"

            st.markdown(f"""
            **{check_name} Check**  
            Status: {status}  
            Allowable: {values['allowable']:.2f} {units}  
            Actual: {values['actual']:.2f} {units}  
            ---
            """)

    with col2:
        try:
            diagram = Image.new('RGB', (500, 400), 'white')
            draw = ImageDraw.Draw(diagram)
            scale = 2
            center_x, center_y = 250, 200

            # Main plate
            draw.ellipse([(center_x - R * scale, center_y - R * scale),
                          (center_x + R * scale, center_y + R * scale)],
                         outline='black', width=2)

            # Hole
            draw.ellipse([(center_x - dh / 2 * scale, center_y - dh / 2 * scale),
                          (center_x + dh / 2 * scale, center_y + dh / 2 * scale)],
                         fill='gray', outline='black')

            # Cheek plates
            cheek_height = r_val * scale * 2
            draw.rectangle([(center_x - R * scale - t_val * scale, center_y - cheek_height / 2),
                            (center_x - R * scale, center_y + cheek_height / 2)],
                           outline='blue', width=2)
            draw.rectangle([(center_x + R * scale, center_y - cheek_height / 2),
                            (center_x + R * scale + t_val * scale, center_y + cheek_height / 2)],
                           outline='blue', width=2)

            # Base plate
            draw.rectangle([(center_x - l_val / 2 * scale, center_y + R * scale),
                            (center_x + l_val / 2 * scale, center_y + R * scale + T * scale)],
                           fill='lightgray', outline='black')

            # Texts
            font = ImageFont.load_default()
            draw.text((center_x - R * scale, center_y + R * scale + 5), f'R: {R}', fill='black', font=font)
            draw.text((center_x - dh / 2 * scale, center_y + 25), f'dh: {dh}', fill='black', font=font)
            draw.text((center_x - l_val / 2 * scale, center_y + R * scale + T * scale + 5), f'l: {l_val}', fill='black', font=font)
            draw.text((center_x - R * scale - t_val * scale - 15, center_y - cheek_height / 2), f't: {t_val}', fill='black', font=font)

            # Display and download
            st.image(diagram, caption="Pad-Eye Schematic", use_container_width=True)
            img_bytes = io.BytesIO()
            diagram.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            st.download_button(
                label="Download Diagram",
                data=img_bytes.getvalue(),
                file_name="padeye_design.png",
                mime="image/png"
            )
        except Exception as e:
            st.warning(f"Could not generate diagram: {str(e)}")

# Overall safety status
if "safety_checks" in locals() and isinstance(safety_checks, dict):
    try:
        all_passed = all(
            isinstance(check, dict) and check.get("passed", False)
            for name, check in safety_checks.items()
            if not (name == "Weld" and (r_val <= 0 or twc <= 0))
        )
        if all_passed:
            st.success("✅ ALL DESIGN CHECKS PASSED - DESIGN IS SAFE")
        else:
            st.error("❌ SOME DESIGN CHECKS FAILED - REVIEW DESIGN PARAMETERS")
    except Exception as e:
        st.warning(f"Could not evaluate final safety status: {str(e)}")



# Shackle Selection Recommendation
st.header("Shackle Selection")
if Ps <= Psh:
    st.success(f"Recommended Shackle: {selected_shackle} with SWL {Psh:.2f} kN is adequate for static sling load ({Ps:.2f} kN).")
else:
    st.error(f"Warning: {selected_shackle} with SWL {Psh:.2f} kN is NOT adequate for static sling load ({Ps:.2f} kN).")