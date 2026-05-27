import numpy as np
import matplotlib.pyplot as plt

class LoiteringMunitionEngine:
    def __init__(self):
        self.T_amb = 288.15    # Sea-level ambient temperature (K)
        self.P_amb = 101325.0  # Sea-level ambient pressure (Pa)
        self.gamma = 1.4       # Ratio of specific heats (Air)
        self.cp = 1004.5       # Specific heat capacity (J/kg*K)
        self.h_fuel = 43.1e6   # Jet-A heating value (J/kg)
        self.eta_c = 0.82      # Small-scale compressor polytropic efficiency
        self.eta_t = 0.85      # Small-scale turbine efficiency

        # --- Physical Hardware Constraints ---
        self.D_wheel = 0.080   # 80mm Impeller Diameter dictated by 5-inch launch tube
        self.psi = 0.935        # Assumed blade work coefficient (loading factor)

    def run_cycle(self, opr, tit):
        # 1. Compression (Station 2 to 3)
        T3_ideal = self.T_amb * (opr ** ((self.gamma - 1) / self.gamma))
        T3 = self.T_amb + (T3_ideal - self.T_amb) / self.eta_c
        w_comp = self.cp * (T3 - self.T_amb)
        
        # 2. Combustion (Station 3 to 4)
        # Fuel-air ratio via energy balance
        f = (self.cp * (tit - T3)) / (self.h_fuel - self.cp * tit)
        if f < 0 or f > 0.068: # Outside flammable/physical limits
            return None, None, None

        # 3. Work Matching / Turbine Expansion (Station 4 to 5)
        # Turbine must generate exactly enough work to drive the compressor
        w_turb = w_comp / (1.0 + f)
        T5 = tit - (w_turb / self.cp)
        
        # Isentropic pressure drop across turbine
        P4 = self.P_amb * opr
        P5 = P4 * ((1.0 - (1.0 - T5/tit)/self.eta_t) ** (self.gamma / (self.gamma - 1)))
        
        # 4. Nozzle Expansion (Station 5 to 9)
        # Final jet kinetic energy conversion
        T9_ideal = T5 * ((self.P_amb / P5) ** ((self.gamma - 1) / self.gamma))
        V_jet = np.sqrt(max(0.0, 2 * self.cp * self.eta_t * (T5 - T9_ideal)))
        
        # 5. Core Performance Metrics
        specific_thrust = V_jet  # Net thrust per unit air mass flow (N/kg/s)
        f_sfc = (f / specific_thrust) * 3600.0  # TSFC converted to kg/N/hr
        
        return specific_thrust, f_sfc, opr
    
    def calculate_hardware_rpm(self, chosen_opr):
        """Bridges 0D Thermodynamics to 3D Physical Hardware Limits"""
        # Calculate ideal compressor exit temperature for the chosen design point
        T3_ideal = self.T_amb * (chosen_opr ** ((self.gamma - 1) / self.gamma))
        T3 = self.T_amb + (T3_ideal - self.T_amb) / self.eta_c
        
        # Specific work required by the compressor (J/kg)
        w_comp = self.cp * (T3 - self.T_amb)
        
        # Euler Turbomachinery Relationship: w_comp = psi * U_tip^2
        # Solve for required linear blade tip speed (m/s)
        U_tip = np.sqrt(w_comp / self.psi)
        
        # Convert linear tip speed to rotational velocity (RPM) based on wheel diameter
        # RPM = (U_tip * 60) / (pi * D)
        rpm = (U_tip * 60) / (np.pi * self.D_wheel)
        
        return U_tip, rpm

# --- Initialize Engine Architecture ---
engine = LoiteringMunitionEngine()
opr_sweep = np.linspace(1.5, 6.0, 300)

# Build out data strictly targeting our 1300K physical material cap
thrust_data = []
tsfc_data = []
opr_mapped = []

for opr in opr_sweep:
    fn, sfc, o = engine.run_cycle(opr, 1300)
    if fn is not None:
        thrust_data.append(fn)
        tsfc_data.append(sfc)
        opr_mapped.append(o)

# Store for our interactive custom tracker
curve_context = {'x': thrust_data, 'y': tsfc_data, 'opr': opr_mapped, 'tit': 1300}

# --- Plot Engineering Design Space ---
fig, ax = plt.subplots(figsize=(11, 5))

# Plot the 1300K solid uncooled Inconel limit line
ax.plot(thrust_data, tsfc_data, color='#E67E22', linewidth=3, label='Material Limit: TIT = 1300K')

# Calculate and Plot Selected Design Anchor (OPR 4.0)
F_design, sfc_design, _ = engine.run_cycle(4.0, 1300)
ax.plot(F_design, sfc_design, marker='o', markersize=10, color='red', zorder=10, 
        label='Selected Architecture Point (OPR = 4.0)')

# Shade the Aerodynamic Instability Zone (OPR > 4.5)
F_limit, _, _ = engine.run_cycle(4.5, 1300)
ax.axvspan(F_limit, max(thrust_data) + 50, color='#FFCCCC', alpha=0.5, zorder=1)
ax.text(F_limit + 10, 0.155, "Single-Stage Limit\n(Shockwaves Form)", 
        color='darkred', fontweight='bold', fontsize=10)

# Clean up axes and frame style
ax.set_title('Propulsion Design Space: Optimizing OPR Under Thermal & Aerodynamic Constraints', 
             fontsize=12, fontweight='bold', pad=15)
ax.set_xlabel('Specific Thrust (N/kg/s)', fontsize=11, labelpad=8)
ax.set_ylabel('TSFC (kg/N/hr) [Lower = More Efficient]', fontsize=11, labelpad=8)
ax.grid(True, linestyle=':', alpha=0.6)
ax.set_xlim(min(thrust_data) - 20, max(thrust_data) + 20)
ax.set_ylim(0.05, 0.22)

# --- Dynamic Coordinate Hover Interaction ---
def format_coord(x, y):
    dx = np.array(curve_context['x']) - x
    dy = (np.array(curve_context['y']) - y) * 1000 # Scaled for distance matching
    distances = np.sqrt(dx**2 + dy**2)
    idx = np.argmin(distances)
    
    # Only snap if the cursor is reasonably close to the curve trace
    if distances[idx] < 35:
        return f"Thrust={curve_context['x'][idx]:.1f} N/kg/s, TSFC={curve_context['y'][idx]:.4f} kg/N/hr  [ OPR={curve_context['opr'][idx]:.2f} @ {curve_context['tit']}K ]"
    else:
        return f"Thrust={x:.1f}, TSFC={y:.4f}"

ax.format_coord = format_coord

ax.legend(loc='upper right', frameon=True, shadow=False)
plt.tight_layout()

print("--> Close the plot window to proceed to Phase 2 (Hardware Translation)...")
plt.show()
	
# --- PHASE 2: HARDWARE INTERACTIVE PROMPT ---
print("\n" + "="*60)
print("             PHASE 2: THERMO-TO-MECHANICAL TRANSLATION          ")
print("="*60)
try:
    user_input = input(f"Enter target Overall Pressure Ratio (Suggested: 4.0 for engineering margin): ")
    chosen_opr = float(user_input)
except ValueError:
    print("Invalid input. Defaulting to optimized target OPR = 4.0")
    chosen_opr = 4.0
# Run hardware translation math
tip_speed, required_rpm = engine.calculate_hardware_rpm(chosen_opr)
print("\n[SYSTEM CALCULATIONS]:")
print(f"  Chosen Engine OPR   : {chosen_opr:.2f}")
print(f"  Impeller Diameter   : {engine.D_wheel * 1000:.1f} mm [Launch Tube Constrained]")
print(f"  Calculated Tip Speed: {tip_speed:.1f} m/s (Mach {tip_speed/340.3:.2f} subsonic fluid profile)")
print(f"  REQUIRED ROTOR SPEED: {required_rpm:,.0f} RPM")
print("="*60)
print(f"--> Input {required_rpm:,.0f} RPM into your Ansys structural velocity boundary condition to verify yield strength margin.")
print("="*60)