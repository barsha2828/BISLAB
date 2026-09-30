import random

# --- 1. USER INPUT & MENU OPTIONS ---
print("--- Classroom Group Formation Setup ---")
num_students = int(input("Enter total number of students (e.g., 8): "))
group_size = int(input("Enter target group size (e.g., 4): "))

NUM_GROUPS = num_students // group_size
GROUP_SIZE = group_size

# Menu mapping for skill selection
SKILL_MENU = {"1": "Beginner", "2": "Intermediate", "3": "Advanced"}

STUDENTS = []
print("\n--- Skill Selection by Roll Number ---")
print("Options: 1 = Beginner | 2 = Intermediate | 3 = Advanced")

for i in range(num_students):
    # Prompt for skill input roll number wise
    while True:
        choice = input(f"Select skill for Roll No {i+1} (1, 2, or 3): ").strip()
        if choice in SKILL_MENU:
            STUDENTS.append({"id": f"Roll No {i+1}", "rank": int(choice), "label": SKILL_MENU[choice]})
            break
        print("Invalid choice. Please enter 1, 2, or 3.")

# --- 2. FITNESS FUNCTION ---
def get_fitness(chromosome):
    """Mixes skills (rewards high variance) and enforces strict group sizes."""
    groups = {i: [] for i in range(NUM_GROUPS)}
    for s_idx, g_id in enumerate(chromosome):
        groups[g_id].append(STUDENTS[s_idx]["rank"])
    
    score = sum((max(g) - min(g)) for g in groups.values() if g)
    size_penalty = sum(-10 * abs(len(g) - GROUP_SIZE) for g in groups.values())
    return score + size_penalty

# --- 3. POPULATION INITIALIZATION ---
base = list(range(NUM_GROUPS)) * GROUP_SIZE
while len(base) < len(STUDENTS):
    base.append(random.randint(0, NUM_GROUPS - 1))
pop = [random.sample(base, len(STUDENTS)) for _ in range(30)]

# --- 4. EVOLUTIONARY LOOP ---
for _ in range(50):
    pop = sorted(pop, key=get_fitness, reverse=True)
    next_gen = pop[:2]  # Elitism
    
    while len(next_gen) < 30:
        p1, p2 = random.choice(pop[:10]), random.choice(pop[:10])
        child = [p1[i] if random.random() < 0.5 else p2[i] for i in range(len(p1))]
        
        if random.random() < 0.1:
            i, j = random.sample(range(len(child)), 2)
            child[i], child[j] = child[j], child[i]
            
        next_gen.append(child)
    pop = next_gen

# --- 5. CLEAN, CONCISE OUTPUT ---
best = max(pop, key=get_fitness)
print("\n--- FINAL OPTIMIZED GROUPS ---")
for g in range(NUM_GROUPS):
    members = [STUDENTS[i] for i, gid in enumerate(best) if gid == g]
    member_strings = [f"{m['id']} ({m['label']})" for m in members]
    print(f"Group {g+1}: {', '.join(member_strings)}")


