import numpy as np
import matplotlib.pyplot as plt

class Turbojet:
    def __init__(self):
        self.gamma_c = 1.4; self.cp_c = 1004
        self.gamma_h = 1.33; self.cp_h = 1150
        self.eta_comp = 0.85; self.eta_comb = 0.98; self.LHV_fuel = 43e6 
        self.max_tip_speed = 550 

    def run_cycle(self, OPR, TIT):
        Ta = 288.15; Pa = 101325
        T2 = Ta
        T3_ideal = T2 * (OPR ** ((self.gamma_c - 1) / self.gamma_c))
        T3 = T2 + (T3_ideal - T2) / self.eta_comp
        w_comp = self.cp_c * (T3 - T2)
        T4 = TIT
        q_in = self.cp_h * (T4 - T3)
        f = q_in / (self.LHV_fuel * self.eta_comb)
        w_turb = w_comp
        T5 = T4 - (w_turb / self.cp_h)
        P5 = (Pa * OPR * 0.96) * ((T5 / T4) ** (self.gamma_h / (self.gamma_h - 1)))
        if P5 < Pa: return None, None, None
        T8 = T5 * (Pa / P5) ** ((self.gamma_h - 1) / self.gamma_h)
        V_exit = np.sqrt(2 * self.cp_h * (T5 - T8))
        F_spec = V_exit
        TSFC = (f / F_spec) * 3600
        return F_spec, TSFC, w_comp

    def solve_sizing(self, target_opr, diameter_mm):
        _, _, w_required = self.run_cycle(target_opr, 1300)
        tip_speed = np.sqrt(w_required / 0.9)
        rpm = (tip_speed * 60) / (np.pi * (diameter_mm / 1000.0))
        status = "OK" if tip_speed < self.max_tip_speed else "FAIL (Burst)"
        return rpm, tip_speed, status

engine = Turbojet()

# --- PLOTTING LOGIC (Multi-Line + Red Zone) ---
ratios = np.linspace(2, 10, 60) # Show up to 10 to demonstrate the linear trend
TIT_values = [1100, 1300, 1500, 1700] 

fig, ax = plt.subplots(figsize=(10, 7))

# Plot all temperature lines
for temp in TIT_values:
    thrusts, tsfcs = [], []
    for r in ratios:
        F, sfc, w = engine.run_cycle(r, temp)
        if F is not None:
            thrusts.append(F)
            tsfcs.append(sfc)
    
    # Highlight the 1300K line (Our choice)
    width = 3 if temp == 1300 else 1.5
    alpha = 1.0 if temp == 1300 else 0.6
    ax.plot(thrusts, tsfcs, linewidth=width, alpha=alpha, label=f'TIT={temp}K')

# Mark our Selected Design Point (OPR 4.0 @ 1300K)
F_4, sfc_4, _ = engine.run_cycle(4.0, 1300)
ax.plot(F_4, sfc_4, 'ro', markersize=10, zorder=10, label='Selected Point (OPR=4.0)')

# --- THE "RED ZONE" (Aerodynamic Limit) ---
# We shade everything beyond OPR 4.5
# Find the specific thrust at OPR 4.5 to start the shading
F_limit, _, _ = engine.run_cycle(4.5, 1300)
ax.axvspan(F_limit, 1200, color='red', alpha=0.15, label='Aerodynamic Limit (OPR > 4.5)')
ax.text(F_limit + 20, 0.16, "Single-Stage Limit\n(Shockwaves Form)", color='darkred', fontweight='bold')

plt.title('Design Space: Balancing Efficiency vs. Complexity')
plt.xlabel('Specific Thrust (N/kg/s)')
plt.ylabel('TSFC (kg/N/hr)')
plt.grid(True)
plt.legend(loc='upper right')
plt.show(block=False) 

# --- INTERACTIVE DECISION ---
print("\n" + "="*40)
print("   ENGINEERING DECISION POINT")
print("="*40)
try:
    user_opr = float(input(">> Enter your selected Pressure Ratio (e.g., 4.0): "))
except ValueError:
    user_opr = 4.0

packaging_limit = 80.0 
print(f"\n--- CONSTRAINT SOLVER (Target OPR = {user_opr}) ---")
rpm, tip_speed, status = engine.solve_sizing(user_opr, packaging_limit)
print(f"REQUIRED SPECS: RPM={rpm:.0f} | Tip Speed={tip_speed:.0f} m/s | Status={status}")