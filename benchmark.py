"""Benchmark: A* vs GBFS on fixed seeded maps with rough terrain.
Run from the project folder:  python benchmark.py
Writes results.csv and prints a summary table."""
import csv
import random
from core.grid import Grid, CellState
from core.algorithms import solve_instant
from core.heuristics import HeuristicType as H

ROWS, COLS, WALL_DENSITY, ROUGH_PROB, ROUGH_COST = 20, 20, 0.20, 0.25, 5.0
N_MAPS = 10
CONFIGS = [("A*", "ASTAR", H.MANHATTAN, "Manhattan"),
           ("A*", "ASTAR", H.EUCLIDEAN, "Euclidean"),
           ("GBFS", "GBFS", H.MANHATTAN, "Manhattan"),
           ("GBFS", "GBFS", H.EUCLIDEAN, "Euclidean")]


def make_map(seed):
    random.seed(seed)
    g = Grid(ROWS, COLS)
    g.generate_random_maze(WALL_DENSITY)
    for cell in g.all_cells():
        if cell.state == CellState.EMPTY and random.random() < ROUGH_PROB:
            g.set_cost(cell.row, cell.col, ROUGH_COST)
    return g


def main():
    rows, seed, used = [], 0, 0
    while used < N_MAPS:
        seed += 1
        g = make_map(seed)
        if not solve_instant(g, "ASTAR", H.MANHATTAN).success:
            continue            # skip unsolvable maps
        used += 1
        for name, key, ht, hname in CONFIGS:
            r = solve_instant(g, key, ht)
            rows.append(dict(map_seed=seed, algorithm=name, heuristic=hname,
                             path_cost=r.path_cost, path_length=len(r.path) - 1,
                             nodes_expanded=r.nodes_visited,
                             time_ms=r.execution_time_ms))
    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"{N_MAPS} maps, {ROWS}x{COLS}, walls {WALL_DENSITY:.0%}, rough {ROUGH_PROB:.0%} (cost {ROUGH_COST:g})\n")
    print(f"{'Algorithm':<6} {'Heuristic':<10} {'Avg cost':>9} {'Avg length':>11} {'Avg nodes':>10} {'Avg ms':>8}")
    for name, _, _, hname in CONFIGS:
        sel = [x for x in rows if x["algorithm"] == name and x["heuristic"] == hname]
        n = len(sel)
        print(f"{name:<6} {hname:<10} {sum(x['path_cost'] for x in sel)/n:>9.1f} "
              f"{sum(x['path_length'] for x in sel)/n:>11.1f} "
              f"{sum(x['nodes_expanded'] for x in sel)/n:>10.1f} "
              f"{sum(x['time_ms'] for x in sel)/n:>8.3f}")


if __name__ == "__main__":
    main()
