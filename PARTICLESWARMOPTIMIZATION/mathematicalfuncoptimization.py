import numpy as np

def pso(func, bounds, num_particles=30, max_iter=50, minimize=True):
    bounds = np.array(bounds)
    dim = len(bounds)
    
    pos = np.random.uniform(bounds[:, 0], bounds[:, 1], (num_particles, dim))
    vel = np.random.uniform(-1, 1, (num_particles, dim))
    
    pbest_pos = np.copy(pos)
    pbest_score = np.array([func(p) for p in pos]) * (1 if minimize else -1)
    
    gbest_pos = np.copy(pbest_pos[np.argmin(pbest_score)])
    gbest_score = np.min(pbest_score)
    
    w, c1, c2 = 0.5, 1.5, 1.5
    for _ in range(max_iter):
        r1, r2 = np.random.rand(num_particles, dim), np.random.rand(num_particles, dim)
        vel = w * vel + c1 * r1 * (pbest_pos - pos) + c2 * r2 * (gbest_pos - pos)
        pos = np.clip(pos + vel, bounds[:, 0], bounds[:, 1])
        
        curr_scores = np.array([func(p) for p in pos]) * (1 if minimize else -1)
        
        better_mask = curr_scores < pbest_score
        pbest_pos[better_mask] = pos[better_mask]
        pbest_score[better_mask] = curr_scores[better_mask]
        
        if np.min(curr_scores) < gbest_score:
            gbest_pos = np.copy(pos[np.argmin(curr_scores)])
            gbest_score = np.min(curr_scores)
            
    return gbest_pos, gbest_score * (1 if minimize else -1)

if __name__ == "__main__":
    print("--- Upgraded PSO Optimization Tool ---")
    print("Example formula to copy: (x - 2)**2 + (y - 3)**2")
    
    # 1. Get user formula
    formula = input("\nEnter your function formula (using x, y, z etc.): ")
    
    # 2. Automatically detect dimensions based on common variables
    # Order: x, y, z, then a, b, c...
    variable_order = ['x', 'y', 'z'] + [chr(i) for i in range(97, 123) if chr(i) not in ['x', 'y', 'z']]
    detected_vars = [v for v in variable_order if v in formula]
    dims = len(detected_vars)
    
    if dims == 0:
        print("Error: Could not detect any variables like x, y, or z in your formula.")
        exit()
        
    print(f"-> Detected {dims} variables: {', '.join(detected_vars)}")
    
    # 3. Create a wrapper function that maps array indices to the chosen text variables
    def user_function(vector):
        local_context = {var: vector[i] for i, var in enumerate(detected_vars)}
        local_context['np'] = np  # Allows using math functions like np.sin(x)
        return eval(formula, {}, local_context)
    
    # 4. Get limits for each detected variable
    bounds = []
    for var in detected_vars:
        low = float(input(f"  Enter MIN limit for '{var}': "))
        high = float(input(f"  Enter MAX limit for '{var}': "))
        bounds.append((low, high))
        
    # 5. Choose Goal
    mode = input("Do you want to 'minimize' or 'maximize'? ").strip().lower()
    is_minimize = mode != "maximize"
    
    # Execute
    best_coords, best_val = pso(user_function, bounds, minimize=is_minimize)
    
    print("\n--- RESULTS ---")
    for i, var in enumerate(detected_vars):
        print(f"Optimal {var}: {best_coords[i]:.6f}")
    print(f"Target value reached: {best_val:.6f}")
