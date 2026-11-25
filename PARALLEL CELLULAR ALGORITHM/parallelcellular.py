import time
import random
import struct
import tkinter as tk
from multiprocessing import Pool, cpu_count

# Global grid reference for worker processes
_WORKER_GRID = None
_WORKER_ROWS = 0
_WORKER_COLS = 0


def init_worker(grid):
    global _WORKER_GRID, _WORKER_ROWS, _WORKER_COLS
    _WORKER_GRID = grid
    _WORKER_ROWS = len(grid)
    _WORKER_COLS = len(grid[0])


# 1. Generate a deterministic 2D grid with random obstacles
def create_grid(size=200, obstacle_prob=0.28, seed=42):
    rng = random.Random(seed)
    grid = [
        [1 if rng.random() < obstacle_prob else 0 for _ in range(size)]
        for _ in range(size)
    ]
    grid[0][0] = 0
    grid[size - 1][size - 1] = 0
    return grid


# 2. Worker function executed in parallel across CPU cores
def expand_frontier_chunk(args):
    chunk, visited_bytes, worker_id = args
    grid = _WORKER_GRID
    rows = _WORKER_ROWS
    cols = _WORKER_COLS

    local_discoveries = {}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r, c in chunk:
        for dr, dc in directions:
            nr = r + dr
            nc = c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] == 0 and visited_bytes[nr * cols + nc] == 0:
                    if (nr, nc) not in local_discoveries:
                        local_discoveries[(nr, nc)] = ((r, c), worker_id)

    return local_discoveries


# 3. Level-Synchronous Parallel BFS Controller
def run_bfs(grid, num_workers=1):
    rows = len(grid)
    cols = len(grid[0])
    start = (0, 0)
    goal = (rows - 1, cols - 1)

    visited = bytearray(rows * cols)
    worker_map = [[0] * cols for _ in range(rows)]
    parent_map = {}

    visited[start[0] * cols + start[1]] = 1
    worker_map[start[0]][start[1]] = 1
    frontier = [start]
    nodes_explored = 0

    start_time = time.perf_counter()

    if num_workers == 1:
        init_worker(grid)
        pool = None
    else:
        pool = Pool(processes=num_workers, initializer=init_worker, initargs=(grid,))

    try:
        while frontier:
            if visited[goal[0] * cols + goal[1]] == 1:
                break

            nodes_explored += len(frontier)

            if num_workers == 1:
                results = [expand_frontier_chunk((frontier, visited, 1))]
            else:
                chunk_size = max(1, (len(frontier) + num_workers - 1) // num_workers)
                tasks = []
                for idx in range(num_workers):
                    sub_chunk = frontier[idx * chunk_size : (idx + 1) * chunk_size]
                    if sub_chunk:
                        tasks.append((sub_chunk, visited, idx + 1))
                results = pool.map(expand_frontier_chunk, tasks)

            # Synchronously merge discoveries from all workers into the next wave
            next_frontier = []
            for res in results:
                for (nr, nc), (parent, w_id) in res.items():
                    flat_idx = nr * cols + nc
                    if visited[flat_idx] == 0:
                        visited[flat_idx] = 1
                        parent_map[(nr, nc)] = parent
                        worker_map[nr][nc] = w_id
                        next_frontier.append((nr, nc))

            frontier = next_frontier
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    elapsed = time.perf_counter() - start_time

    # Reconstruct shortest path from goal back to start
    path = []
    curr = goal
    if visited[goal[0] * cols + goal[1]] == 1:
        while curr != start:
            path.append(curr)
            curr = parent_map[curr]
        path.append(start)
        path.reverse()

    return path, worker_map, nodes_explored, elapsed


# 4. Build BMP Image Bytes & Display Directly Inside Python via Tkinter
def build_and_show_image(grid, worker_map, path, num_workers, scale=3, filename="parallel_bfs_output.bmp"):
    rows = len(grid)
    cols = len(grid[0])
    path_set = set(path)

    palette = {
        -1: (25, 25, 25),       # Wall: Dark Charcoal
        0: (245, 245, 245),     # Unvisited: Off-White
        1: (78, 121, 167),      # Worker 1: Blue
        2: (242, 142, 43),      # Worker 2: Orange
        3: (89, 161, 79),       # Worker 3: Green
        4: (237, 201, 72),      # Worker 4: Yellow
        5: (176, 122, 161),     # Worker 5: Purple
        6: (118, 183, 178),     # Worker 6: Teal
        7: (255, 157, 167),     # Worker 7: Pink
        8: (156, 117, 95),      # Worker 8: Brown
    }

    img_w = cols * scale
    img_h = rows * scale
    row_padding = (4 - (img_w * 3) % 4) % 4
    row_bytes = img_w * 3 + row_padding
    pixel_data_size = row_bytes * img_h
    file_size = 54 + pixel_data_size

    header = struct.pack(
        "<2sIHHIIiiHHIIiiII",
        b"BM",
        file_size,
        0,
        0,
        54,
        40,
        img_w,
        -img_h,
        1,
        24,
        0,
        pixel_data_size,
        2835,
        2835,
        0,
        0,
    )

    # Also build PPM format in memory so Tkinter PhotoImage renders natively on all OSes
    ppm_header = f"P6\n{img_w} {img_h}\n255\n".encode("ascii")
    ppm_pixels = bytearray()
    bmp_pixels = bytearray()

    for r in range(rows):
        bmp_row = bytearray()
        ppm_row = bytearray()
        for c in range(cols):
            if (r, c) == (0, 0):
                rgb = (0, 230, 0)          # Start: Bright Green
            elif (r, c) == (rows - 1, cols - 1):
                rgb = (255, 0, 0)          # Goal: Bright Red
            elif (r, c) in path_set:
                rgb = (220, 0, 220)        # Shortest Path: Magenta
            elif grid[r][c] == 1:
                rgb = palette[-1]
            else:
                w_id = worker_map[r][c]
                rgb = palette.get(w_id, (100, 150, 200))

            bmp_row.extend(bytes((rgb[2], rgb[1], rgb[0])) * scale)
            ppm_row.extend(bytes((rgb[0], rgb[1], rgb[2])) * scale)

        bmp_row.extend(b"\x00" * row_padding)
        for _ in range(scale):
            bmp_pixels.extend(bmp_row)
            ppm_pixels.extend(ppm_row)

    with open(filename, "wb") as f:
        f.write(header)
        f.write(bmp_pixels)

    print(f"Image saved to '{filename}' and opening Python viewer window...")

    # Display inside a native Python Tkinter window
    root = tk.Tk()
    root.title(f"Parallel BFS Pathfinding ({num_workers} Workers)")

    photo = tk.PhotoImage(data=ppm_header + bytes(ppm_pixels))
    label = tk.Label(root, image=photo)
    label.image = photo  # Keep reference to prevent garbage collection
    label.pack(padx=10, pady=(10, 5))

    legend_text = (
        f"Grid: {rows}x{cols} | Workers: {num_workers} | Path Length: {len(path)} steps\n"
        "Colors: Blue=Worker 1 | Orange=Worker 2 | Green=Worker 3 | Yellow=Worker 4 | Magenta=Shortest Path"
    )
    info = tk.Label(root, text=legend_text, font=("Arial", 10))
    info.pack(pady=(0, 10))

    root.mainloop()


# 5. Main Execution
if __name__ == "__main__":
    GRID_SIZE = 200
    WORKERS = min(4, cpu_count())

    print(f"Generating {GRID_SIZE}x{GRID_SIZE} grid...")
    grid = create_grid(size=GRID_SIZE, obstacle_prob=0.28, seed=42)

    print("\n--- Sequential BFS (1 Worker) ---")
    seq_path, _, seq_nodes, seq_time = run_bfs(grid, num_workers=1)
    print(f"Nodes Explored : {seq_nodes}")
    print(f"Path Length    : {len(seq_path)} steps")
    print(f"Execution Time : {seq_time:.4f} seconds")

    print(f"\n--- Parallel BFS ({WORKERS} Workers) ---")
    par_path, worker_map, par_nodes, par_time = run_bfs(grid, num_workers=WORKERS)
    print(f"Nodes Explored : {par_nodes}")
    print(f"Path Length    : {len(par_path)} steps")
    print(f"Execution Time : {par_time:.4f} seconds")

    if par_time > 0:
        print(f"Speedup Ratio  : {seq_time / par_time:.2f}x")

    build_and_show_image(grid, worker_map, par_path, WORKERS, scale=3)

