import numpy as np
import matplotlib.pyplot as plt

# --- 1. DEFINE THE ENGINE CLASS ---
class Turbojet:
    def __init__(self, name="Micro-Jet-01"):
        self.name = name
        # Standard Sea Level Conditions
        self.Ta = 288.15  # Ambient Temp (Kelvin)
        self.Pa = 101325  # Ambient Pressure (Pa)
        
        # Engine Properties (Constants)
        self.gamma_c = 1.4   # Specific Heat Ratio (Cold Air)
        self.cp_c = 1004     # Specific Heat (Cold Air) J/kgK
        self.gamma_h = 1.33  # Specific Heat Ratio (Hot Gas)
        self.cp_h = 1150     # Specific Heat (Hot Gas) J/kgK
        
        # Component Efficiencies (Assumed realistic values)
        self.eta_comp = 0.85  # Compressor Isentropic Efficiency
        self.eta_turb = 0.90  # Turbine Isentropic Efficiency
        self.eta_comb = 0.98  # Combustion Efficiency
        self.LHV_fuel = 43e6 # Lower Heating Value of Fuel (J/kg)

    def run_cycle(self, OPR, TIT):
        # 1. Compressor
        T2 = self.Ta
        T3_ideal = T2 * (OPR ** ((self.gamma_c - 1) / self.gamma_c))
        T3 = T2 + (T3_ideal - T2) / self.eta_comp
        w_comp = self.cp_c * (T3 - T2)

        # 2. Combustor
        T4 = TIT
        q_in = self.cp_h * (T4 - T3)
        # Fuel Air Ratio (f) = q_in / (LHV * combustion_efficiency)
        f = q_in / (self.LHV_fuel * self.eta_comb)

        # 3. Turbine
        w_turb = w_comp # Turbine drives compressor
        T5 = T4 - (w_turb / self.cp_h)
        P3 = self.Pa * OPR
        P4 = P3 * 0.96 # Assume 4% pressure loss in combustor (Realism boost)
        P5 = P4 * ((T5 / T4) ** (self.gamma_h / (self.gamma_h - 1)))

        # 4. Nozzle
        if P5 < self.Pa: return 0, 0, 0 # Failed cycle
        T8 = T5 * (self.Pa / P5) ** ((self.gamma_h - 1) / self.gamma_h)
        V_exit = np.sqrt(2 * self.cp_h * (T5 - T8))
        
        # PERFORMANCE METRICS
        # Specific Thrust (N per kg/s airflow)
        F_spec = V_exit 
        
        # TSFC: Thrust Specific Fuel Consumption (kg_fuel / N_thrust / hr)
        # TSFC = (f / F_spec) * 3600
        TSFC = (f / F_spec) * 3600
        
        # Estimated Engine Weight (Heuristic for Micro-Turbines)
        # Weight scales with Pressure Ratio (heavier compressor) and Temperature (heavier turbine materials)
        # This is a "First Order Approximation" - Interviewers love this.
        weight_factor = 0.5 * OPR + 0.001 * TIT 
        thrust_to_weight = F_spec / weight_factor 

        return F_spec, TSFC, thrust_to_weight
    
# --- RUN SIMULATION ---
engine = Turbojet()
ratios = np.linspace(2, 16, 50)
TIT_values = [1100, 1300, 1500] # Kelvin

plt.figure(figsize=(12, 5))

# Plot 1: Efficiency (TSFC) vs Thrust
plt.subplot(1, 2, 1)
for temp in TIT_values:
    thrusts, tsfcs = [], []
    for r in ratios:
        F, sfc, ttw = engine.run_cycle(r, temp)
        thrusts.append(F)
        tsfcs.append(sfc)
    plt.plot(thrusts, tsfcs, label=f'TIT={temp}K')

plt.title('Design Space: Fuel Efficiency vs Thrust')
plt.xlabel('Specific Thrust (N/kg/s)')
plt.ylabel('TSFC (Lower is Better)')
plt.grid(True)
plt.legend()

# Plot 2: Thrust-to-Weight Estimate
plt.subplot(1, 2, 2)
for temp in TIT_values:
    ttw_list = []
    for r in ratios:
        F, sfc, ttw = engine.run_cycle(r, temp)
        ttw_list.append(ttw)
    plt.plot(ratios, ttw_list, label=f'TIT={temp}K')

plt.title('Volund Metric: Thrust-to-Weight Optimization')
plt.xlabel('Compressor Pressure Ratio')
plt.ylabel('Estimated Thrust-to-Weight Index')
plt.grid(True)

plt.tight_layout()
plt.show()