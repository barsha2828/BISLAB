import numpy as np
import matplotlib.pyplot as plt

class CropRotator:
    def __init__(self, crops, costs):
        self.crops = crops
        self.costs = np.array(costs)
        self.n = len(crops)
        self.phero = np.ones((self.n, self.n))
        self.heur = 1.0 / (self.costs + 1e-5)

    def solve(self, ants=30, gens=150):
        best_path, best_cost = None, float('inf')
        for gen in range(gens):
            paths, costs = [], []
            for a in range(ants):
                path = [np.random.randint(self.n)]
                while len(path) < self.n:
                    curr = path[-1]
                    probs = (self.phero[curr] ** 1.0) * (self.heur[curr] ** 2.0)
                    probs[path] = 0
                    if probs.sum() == 0:
                        probs[[c for c in range(self.n) if c not in path]] = 1
                    
                    normalized_probs = probs / probs.sum()
                    
                    # === CORRECTED LOGIC CHANGE ===
                    # Instead of np.random.choice, we use np.argmax to strictly pick the highest value
                    next_crop = np.argmax(normalized_probs)
                    
                    # Live tracker layout matching your request
                    if gen == 0 and a == 0 and len(path) == 1:
                        print("\n==============================================")
                        print("       LIVE ANT PATH DISCOVERY DASHBOARD      ")
                        print("==============================================")
                        print(f"Ant #1 is currently standing at: {self.crops[curr]}")
                        print("Probability wheel breakdown for next options:")
                        
                        # Collect and sort unique choices to cleanly show them
                        for idx, percentage in enumerate(normalized_probs):
                            if idx not in path and percentage > 0.01:
                                print(f" -> Next Choice Option: {self.crops[idx]:<10} | Probability: {percentage*100:.1f}%")
                        
                        print(f"\n[DECISION] Correctly choosing highest option: {self.crops[next_crop]}")
                        print("==============================================\n")

                    path.append(next_crop)
                
                cost = sum(self.costs[path[i]][path[(i+1)%self.n]] for i in range(self.n))
                paths.append(path)
                costs.append(cost)
                if cost < best_cost:
                    best_cost, best_path = cost, path
            
            self.phero *= 0.6
            for p, c in zip(paths, costs):
                for i in range(self.n):
                    self.phero[p[i]][p[(i+1)%self.n]] += 100 / (c + 1e-5)
        return [self.crops[i] for i in best_path], best_cost

if __name__ == "__main__":
    print("==============================================")
    print("      SCALABLE CROP ROTATION OPTIMIZER        ")
    print("==============================================\n")
    
    total_needed = int(input("How many crops/seasons to plan for? (e.g., 40): "))
    base_crops = ["Corn", "Soybeans", "Wheat", "Alfalfa", "Clover", "Oats", "Barley", "Rye"]
    crop_list = [base_crops[i % len(base_crops)] for i in range(total_needed)]
        
    penalty_matrix = []
    for i in range(total_needed):
        row = []
        for j in range(total_needed):
            if i == j:
                row.append(999)
            elif crop_list[i] == crop_list[j]:
                row.append(80)  
            else:
                row.append(int((i + j) % 31 + 10)) 
        penalty_matrix.append(row)
        
    rotator = CropRotator(crop_list, penalty_matrix)
    sequence, score = rotator.solve()
    
    if crop_list in sequence:
        start_idx = sequence.index(crop_list)
        sequence = sequence[start_idx:] + sequence[:start_idx]
        
    avg_penalty = score / total_needed
        
    print("=== Optimized Crop Rotation Schedule ===")
    print(" -> ".join(sequence) + f" -> {sequence} (Cycle complete)")
    print(f"Total Agrotechnical Penalty Score: {int(score)}")
    print(f"Average Penalty Score per Year/Season: {avg_penalty:.2f}")

    # Circular Diagram
    angles = np.linspace(0, 2 * np.pi, total_needed, endpoint=False)
    x = np.cos(angles)
    y = np.sin(angles)
    
    plt.figure(figsize=(9, 9))
    for i in range(total_needed):
        next_i = (i + 1) % total_needed
        plt.annotate('', xy=(x[next_i], y[next_i]), xytext=(x[i], y[i]),
                     arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=1.5, mutation_scale=12))
        
    step_jump = 1 if total_needed <= 15 else (total_needed // 10)
    for i, name in enumerate(sequence):
        if i % step_jump == 0 or i == total_needed - 1:
            plt.text(x[i]*1.15, y[i]*1.15, f"Step {i+1}: {name}", fontsize=9, ha='center', va='center', weight='bold')
            plt.plot(x[i], y[i], 'go', markersize=6)
        else:
            plt.plot(x[i], y[i], 'g.', markersize=4)

    plt.title(f"Simplified Rotation Cycle ({total_needed} Steps)", fontsize=13, weight='bold', pad=15)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
