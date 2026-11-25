import math
import random
import tkinter as tk

random.seed(42)


# 1. Objective Function: Partially Shaded Solar PV Power-Voltage (P-V) Curve
def pv_array_power(voltage):
  v = max(0.0, min(100.0, voltage))
  peak_local_1 = 180.0 * math.exp(-(((v - 25.0) / 8.0) ** 2))
  peak_global = 310.0 * math.exp(-(((v - 58.0) / 10.0) ** 2))
  peak_local_2 = 215.0 * math.exp(-(((v - 85.0) / 7.5) ** 2))
  return peak_local_1 + peak_global + peak_local_2


# 2. Grey Wolf Optimizer (GWO)
def grey_wolf_mppt(n_wolves=12, max_iter=35, lb=0.0, ub=100.0):
  positions = [random.uniform(lb, ub) for _ in range(n_wolves)]
  alpha_pos, alpha_score = 0.0, float("-inf")
  beta_pos, beta_score = 0.0, float("-inf")
  delta_pos, delta_score = 0.0, float("-inf")

  convergence_history = []

  for t in range(max_iter):
    for i in range(n_wolves):
      positions[i] = max(lb, min(ub, positions[i]))
      fitness = pv_array_power(positions[i])

      if fitness > alpha_score:
        delta_score, delta_pos = beta_score, beta_pos
        beta_score, beta_pos = alpha_score, alpha_pos
        alpha_score, alpha_pos = fitness, positions[i]
      elif fitness > beta_score:
        delta_score, delta_pos = beta_score, beta_pos
        beta_score, beta_pos = fitness, positions[i]
      elif fitness > delta_score:
        delta_score, delta_pos = fitness, positions[i]

    convergence_history.append((t + 1, alpha_pos, alpha_score))
    a = 2.0 - t * (2.0 / max_iter)

    for i in range(n_wolves):
      r1, r2 = random.random(), random.random()
      A1, C1 = 2 * a * r1 - a, 2 * r2
      X1 = alpha_pos - A1 * abs(C1 * alpha_pos - positions[i])

      r1, r2 = random.random(), random.random()
      A2, C2 = 2 * a * r1 - a, 2 * r2
      X2 = beta_pos - A2 * abs(C2 * beta_pos - positions[i])

      r1, r2 = random.random(), random.random()
      A3, C3 = 2 * a * r1 - a, 2 * r2
      X3 = delta_pos - A3 * abs(C3 * delta_pos - positions[i])

      positions[i] = (X1 + X2 + X3) / 3.0

  return alpha_pos, alpha_score, convergence_history


# Run Optimization
best_voltage, max_power, history = grey_wolf_mppt()

# 3. Console Text Output
print("=== GWO Solar PV MPPT Optimization Results ===")
print(f"Optimal Operating Voltage (V_mpp): {best_voltage:.4f} V")
print(f"Global Maximum Power (P_mpp):    {max_power:.4f} W\n")
print("Iteration | Best Voltage (V) | Best Power (W)")
print("-" * 45)
for step in range(0, 35, 7):
  it, v_best, p_best = history[step]
  print(f"{it:9d} | {v_best:16.4f} | {p_best:14.4f}")

# 4. Generate Output Image Window using built-in tkinter
root = tk.Tk()
root.title("Solar PV P-V Curve & Grey Wolf MPPT Result")
W, H = 760, 460
pad_l, pad_r, pad_t, pad_b = 70, 30, 50, 60
canvas = tk.Canvas(root, width=W, height=H, bg="white")
canvas.pack()


def to_px(v, p):
  x = pad_l + (v / 100.0) * (W - pad_l - pad_r)
  y = (H - pad_b) - (p / 350.0) * (H - pad_t - pad_b)
  return x, y


# Title & Axes
canvas.create_text(
    W // 2,
    22,
    text="Solar PV Power-Voltage Curve & Grey Wolf MPPT Result",
    font=("Arial", 12, "bold"),
)
canvas.create_line(pad_l, H - pad_b, W - pad_r, H - pad_b, width=2)
canvas.create_line(pad_l, pad_t, pad_l, H - pad_b, width=2)
canvas.create_text(W // 2, H - 18, text="Array Voltage (V)", font=("Arial", 10))
canvas.create_text(
    22, H // 2, text="Power (W)", angle=90, font=("Arial", 10)
)

# Gridlines & Ticks
for v_tick in range(0, 101, 20):
  x, _ = to_px(v_tick, 0)
  canvas.create_line(x, pad_t, x, H - pad_b, fill="#e0e0e0", dash=(3, 3))
  canvas.create_text(x, H - pad_b + 15, text=str(v_tick), font=("Arial", 8))

for p_tick in range(0, 351, 50):
  _, y = to_px(0, p_tick)
  canvas.create_line(pad_l, y, W - pad_r, y, fill="#e0e0e0", dash=(3, 3))
  canvas.create_text(pad_l - 18, y, text=str(p_tick), font=("Arial", 8))

# Plot P-V Curve
pts = []
for i in range(501):
  v = i * 0.2
  pts.extend(to_px(v, pv_array_power(v)))
canvas.create_line(pts, fill="#1f77b4", width=2.5)

# Plot Local Peaks (Orange) & Global Peak (Red)
for lv, lp, label in [(25.0, 180.0, "Local 1"), (85.0, 215.0, "Local 2")]:
  lx, ly = to_px(lv, lp)
  canvas.create_oval(
      lx - 5, ly - 5, lx + 5, ly + 5, fill="#ff7f0e", outline="black"
  )
  canvas.create_text(
      lx,
      ly - 14,
      text=f"{label} ({lp:.0f}W)",
      fill="#b35900",
      font=("Arial", 8, "bold"),
  )

gx, gy = to_px(best_voltage, max_power)
canvas.create_oval(
    gx - 6, gy - 6, gx + 6, gy + 6, fill="#d62728", outline="black"
)
canvas.create_text(
    gx,
    gy - 16,
    text=f"GWO GMPP ({best_voltage:.2f}V, {max_power:.2f}W)",
    fill="#d62728",
    font=("Arial", 9, "bold"),
)

root.mainloop()

