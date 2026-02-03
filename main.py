import numpy as np
import matplotlib.pyplot as plt

class Turbojet:
    def __init__(self, name="Volund-Class MicroJet"):
        self.name = name
        self.Ta = 288.15  # Sea Level Temp (K)
        self.Pa = 101325  # Sea Level Pressure (Pa)
        self.gamma_c = 1.4
        self.cp_c = 1004
        self.gamma_h = 1.33
        self.cp_h = 1150
        self.eta_comp = 0.85
        self.eta_comb = 0.98
        self.LHV_fuel = 43e6 
        
        # MATERIAL PROPERTIES
        self.material_density = 4430 # Ti-6Al-4V (kg/m^3)
        self.max_tip_speed = 550 # m/s (Structural limit)

    def run_cycle_constrained(self, OPR, TIT, target_diameter_mm):
        """
        CONSTRAINT-DRIVEN ANALYSIS:
        Input: Desired Pressure Ratio & Physical Diameter Limit.
        Output: Required RPM & Performance.
        """
        # 1. Thermodynamics (Cycle Requirements)
        T2 = self.Ta
        T3_ideal = T2 * (OPR ** ((self.gamma_c - 1) / self.gamma_c))
        T3 = T2 + (T3_ideal - T2) / self.eta_comp
        w_comp = self.cp_c * (T3 - T2) # Work required per kg of air

        # 2. Aerodynamics (Sizing)
        # We need this much work. How fast must the blade tips move?
        # Work = Work_Factor * U^2  ->  U = sqrt(Work / Work_Factor)
        work_factor = 0.9
        required_tip_speed = np.sqrt(w_comp / work_factor)
        
        # 3. Mechanics (RPM Calculation)
        # Tip Speed = (RPM * pi * Diameter) / 60
        # RPM = (Tip Speed * 60) / (pi * Diameter)
        diameter_m = target_diameter_mm / 1000.0
        required_rpm = (required_tip_speed * 60) / (np.pi * diameter_m)

        # 4. Rest of Cycle (Thrust/Efficiency)
        T4 = TIT
        q_in = self.cp_h * (T4 - T3)
        f = q_in / (self.LHV_fuel * self.eta_comb)
        
        w_turb = w_comp 
        T5 = T4 - (w_turb / self.cp_h)
        P5 = (self.Pa * OPR * 0.96) * ((T5 / T4) ** (self.gamma_h / (self.gamma_h - 1)))
        
        if P5 < self.Pa: return None

        T8 = T5 * (self.Pa / P5) ** ((self.gamma_h - 1) / self.gamma_h)
        V_exit = np.sqrt(2 * self.cp_h * (T5 - T8))
        F_spec = V_exit 
        TSFC = (f / F_spec) * 3600
        
        status = "OK" if required_tip_speed < self.max_tip_speed else "FAIL (Material Burst)"

        return {
            "OPR": OPR,
            "Diameter_mm": target_diameter_mm,
            "Required_RPM": required_rpm,
            "Tip_Speed": required_tip_speed,
            "Thrust_Specific": F_spec,
            "TSFC": TSFC,
            "Status": status
        }

# --- RUN SIMULATION ---
engine = Turbojet()

# "Constraint-Driven" Problem Statement:
# "I have a packaging limit of 80mm. How fast must I spin to get PR 4.0?"
packaging_limit_mm = 80.0 
design_point = engine.run_cycle_constrained(OPR=4.0, TIT=1300, target_diameter_mm=packaging_limit_mm)

print(f"--- CONSTRAINT-DRIVEN DESIGN (Limit={packaging_limit_mm}mm) ---")
print(f"Target Pressure Ratio: {design_point['OPR']}")
print(f"REQUIRED RPM: {design_point['Required_RPM']:.0f}")
print(f"Resulting Tip Speed: {design_point['Tip_Speed']:.2f} m/s")
print(f"Structural Check: {design_point['Status']}")
print(f"Predicted Specific Thrust: {design_point['Thrust_Specific']:.2f} N/kg/s")