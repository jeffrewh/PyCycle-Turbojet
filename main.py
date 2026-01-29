import numpy as np
import matplotlib.pyplot as plt

class TurbojetCycle:
    def __init__(self, T_ambient=288.15, P_ambient=101325, gamma=1.4, cp=1005):
        self.Ta = T_ambient  # Ambient Temp (K)
        self.Pa = P_ambient  # Ambient Pressure (Pa)
        self.gamma = gamma   # Heat capacity ratio
        self.cp = cp         # Specific heat (J/kg*K)

    def calculate_cycle(self, pressure_ratio, T_turbine_inlet):
        # 1. Intake (Assume ideal for simplicity)
        T2 = self.Ta
        P2 = self.Pa

        # 2. Compressor (Isentropic compression)
        # T3/T2 = (P3/P2)^((gamma-1)/gamma)
        P3 = self.Pa * pressure_ratio
        T3 = T2 * (pressure_ratio ** ((self.gamma - 1) / self.gamma))
        
        # Work done by compressor
        W_comp = self.cp * (T3 - T2)

        # 3. Combustion (Add heat to reach Turbine Inlet Temp)
        T4 = T_turbine_inlet
        P4 = P3 # Constant pressure combustion
        Q_in = self.cp * (T4 - T3)

        # 4. Turbine (Work turbine = Work compressor for a turbojet)
        # W_turb = W_comp -> cp(T4 - T5) = cp(T3 - T2)
        T5 = T4 - (T3 - T2)
        P5 = P4 * (T5 / T4) ** (self.gamma / (self.gamma - 1))

        # 5. Nozzle (Expand to ambient)
        # Check for choked flow in real life, but assume ideal expansion here for simplicity
        T6 = T5 * (self.Pa / P5) ** ((self.gamma - 1) / self.gamma)
        V_exit = np.sqrt(2 * self.cp * (T5 - T6))

        # Performance Metrics
        F_specific = V_exit # Thrust per kg/s (assuming V_in approx 0)
        efficiency = (V_exit**2 / 2) / Q_in
        
        return F_specific, efficiency

# --- EXECUTION ---
engine = TurbojetCycle()
ratios = np.linspace(2, 40, 50) # Sweep pressure ratios from 2 to 40
T_combustor = 1400 # 1400 Kelvin Turbine Inlet Temp

results_thrust = []
results_eff = []

for r in ratios:
    thrust, eff = engine.calculate_cycle(r, T_combustor)
    results_thrust.append(thrust)
    results_eff.append(eff)

# --- PLOTTING ---
fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:red'
ax1.set_xlabel('Compressor Pressure Ratio')
ax1.set_ylabel('Specific Thrust (N/kg/s)', color=color)
ax1.plot(ratios, results_thrust, color=color, linewidth=2)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Thermal Efficiency', color=color)
ax2.plot(ratios, results_eff, color=color, linestyle='--', linewidth=2)
ax2.tick_params(axis='y', labelcolor=color)

plt.title(f'Brayton Cycle Optimization (TIT = {T_combustor}K)')
plt.grid(True, alpha=0.3)
plt.show()