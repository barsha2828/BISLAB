import random
import math
import tkinter as tk

random.seed(42)

# 1. Warehouse Depot and 8 Delivery Stops (x, y in km)
depot = (50, 50)
x_coords = (16, 28, 58, 76, 88, 74, 62, 34)
y_coords = (42, 32, 30, 34, 52, 76, 78, 74)
stops = list(zip(x_coords, y_coords))
n_stops = len(stops)

def dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def route_distance(order):
    path = [depot] + [stops[i] for i in order] + [depot]
    return sum(dist(path[i], path[i + 1]) for i in range(len(path) - 1))

# 2. Initialize 15 Host Nests (Candidate Routes)
n_nests = 15
base_indices = list(range(n_stops))
nests = [random.sample(base_indices, n_stops) for _ in range(n_nests)]
fitness = [route_distance(n) for n in nests]

worst_idx_init = fitness.index(max(fitness))
initial_route = list(nests[worst_idx_init])
initial_dist = fitness[worst_idx_init]
history = []

# 3. Run Cuckoo Search Optimization (100 Iterations)
for _ in range(100):
    for i in range(n_nests):
        cand = list(nests[i])
        # Levy Flight step: 2-opt reversal (70%) or stop swap (30%)
        if random.random() < 0.7:
            a, b = sorted(random.sample(range(n_stops), 2))
            cand[a:b + 1] = reversed(cand[a:b + 1])
        else:
            a, b = random.sample(range(n_stops), 2)
            cand[a], cand[b] = cand[b], cand[a]

        f_new = route_distance(cand)
        if f_new < fitness[i]:
            nests[i] = cand
            fitness[i] = f_new

    # Abandon worst 25% of nests (pa = 0.25)
    n_abandon = int(0.25 * n_nests)
    ranked = sorted(range(n_nests), key=lambda k: fitness[k])
    for idx in ranked[-n_abandon:]:
        nests[idx] = random.sample(base_indices, n_stops)
        fitness[idx] = route_distance(nests[idx])

    history.append(min(fitness))

best_idx = fitness.index(min(fitness))
best_route = nests[best_idx]
best_dist = fitness[best_idx]
reduction = (1 - best_dist / initial_dist) * 100

# 4. Draw Output Picture in a Window
root = tk.Tk()
root.title("Cuckoo Search Algorithm - Logistics & Route Optimization Output")
canvas = tk.Canvas(root, width=920, height=580, bg="white")
canvas.pack()

def map_pt(pt, offset_x):
    px = offset_x + (pt[0] / 100.0) * 380
    py = 330 - (pt[1] / 100.0) * 260
    return px, py

def draw_map(offset_x, title, order, color, dash_style, show_numbers):
    canvas.create_rectangle(offset_x + 15, 50, offset_x + 405, 320, outline="#cccccc", fill="#f9fbfd")
    canvas.create_text(offset_x + 210, 30, text=title, font=("Arial", 11, "bold"), fill="#111111")

    path = [depot] + [stops[i] for i in order] + [depot]
    for i in range(len(path) - 1):
        x1, y1 = map_pt(path[i], offset_x)
        x2, y2 = map_pt(path[i + 1], offset_x)
        canvas.create_line(x1, y1, x2, y2, fill=color, width=2.5, dash=dash_style)

    # Draw Stops
    for idx, s in enumerate(stops):
        sx, sy = map_pt(s, offset_x)
        fill_c = "#2ca02c" if show_numbers else "#666666"
        canvas.create_oval(sx - 6, sy - 6, sx + 6, sy + 6, fill=fill_c, outline="black")

    if show_numbers:
        for step, stop_idx in enumerate(order, 1):
            sx, sy = map_pt(stops[stop_idx], offset_x)
            canvas.create_text(sx, sy - 14, text=str(step), font=("Arial", 9, "bold"), fill="#000000")

    # Draw Depot
    dx, dy = map_pt(depot, offset_x)
    canvas.create_rectangle(dx - 8, dy - 8, dx + 8, dy + 8, fill="#1f4e78", outline="black")
    canvas.create_text(dx, dy + 16, text="Depot", font=("Arial", 8, "bold"), fill="#1f4e78")

draw_map(20, f"BEFORE: Initial Route ({initial_dist:.1f} km)", initial_route, "#d62728", (4, 3), False)
draw_map(470, f"AFTER: Optimized Route ({best_dist:.1f} km | -{reduction:.1f}%)", best_route, "#2ca02c", None, True)

# Draw Convergence Graph at Bottom
canvas.create_rectangle(70, 380, 860, 530, outline="#cccccc", fill="#f9fbfd")
canvas.create_text(465, 362, text="Cuckoo Search Convergence Output (100 Iterations)", font=("Arial", 11, "bold"))
canvas.create_text(465, 552, text="Iterations (1 to 100)", font=("Arial", 9))
canvas.create_text(35, 455, text="Dist\n(km)", font=("Arial", 9))

min_h, max_h = min(history), max(history)
span = max(max_h - min_h, 1.0)
pts = []
for step, val in enumerate(history):
    cx = 85 + (step / 99.0) * 760
    cy = 515 - ((val - min_h) / span) * 115
    pts.extend((cx, cy))
canvas.create_line(*pts, fill="#1f4e78", width=2.5)

root.mainloop()
