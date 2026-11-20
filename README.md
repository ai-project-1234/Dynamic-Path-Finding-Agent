# Dynamic Pathfinding Agent

> A real-time grid navigation agent built with Python + Pygame.
> Implements **Greedy Best-First Search** and **A\*** with live visualization,
> interactive map editing, **terrain-cost (energy-aware) planning**, and a dynamic obstacle
> mode with automatic re-planning.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Project Structure](#project-structure)
- [How to Use](#how-to-use)
- [Terrain Costs](#terrain-costs)
- [Algorithms](#algorithms)
- [Heuristics](#heuristics)
- [Dynamic Mode](#dynamic-mode)
- [Metrics](#metrics)
- [Visual Legend](#visual-legend)
- [Keyboard and Mouse Controls](#keyboard-and-mouse-controls)
- [Configuration](#configuration)
- [Testing](#testing)
- [Benchmark and Results](#benchmark-and-results)
- [Screenshots](#screenshots)
- [Future Work](#future-work)
- [Team](#team)

---

## Features

| Feature | Details |
|---|---|
| **Two Search Algorithms** | Greedy Best-First Search (GBFS) and A* Search |
| **Two Heuristics** | Manhattan Distance and Euclidean Distance, switchable at runtime |
| **Terrain Costs** | Normal cells cost 1, rough cells cost 5; A* plans the cheapest route, not just the shortest |
| **Step-by-step Visualization** | Watch the frontier expand and path form in real time |
| **Dynamic Obstacle Mode** | Obstacles spawn mid-transit; agent detects and re-plans instantly, using the same terrain costs |
| **Interactive Map Editor** | Left-click or drag to paint and erase walls; right-click to paint rough terrain |
| **Random Maze Generation** | Configurable obstacle density (5% to 65%) |
| **Live Metrics Dashboard** | Nodes visited, weighted path cost, execution time, re-plan count, steps taken |
| **Adjustable Speed** | Independent sliders for visualization speed and agent movement speed |
| **Resizable Grid** | From 5x5 up to 40x60, configured via sliders |
| **Unit Tests and Benchmark** | `tests/` for terrain-cost behaviour and `benchmark.py` for A* vs GBFS comparison |

---

## Installation

**Requirements:** Python 3.9 or higher

### 1. Clone the repository

```bash
git clone https://github.com/shivampoojanyadav/Dynamic-Path-Finding-Agent.git
cd Dynamic-Path-Finding-Agent
```

### 2. Install dependencies

A `requirements.txt` file is included. Install everything with a single command:

```bash
pip install -r requirements.txt
```

> This installs `pygame`, the only external dependency the project needs.

> **Very new Python versions (for example 3.14):** if `pygame` fails to build, install
> `pygame-ce` instead with `pip install pygame-ce`. It is imported as `pygame`, so the
> project runs unchanged.

---

## Running the App

```bash
python main.py
```

The application window will open immediately at **1280 x 820** pixels with a default 20x20 grid.

---

## Project Structure

```
Dynamic-Path-Finding-Agent/
│
├── main.py                    # Entry point — initializes Pygame and launches the app
├── benchmark.py               # A* vs GBFS comparison on fixed seeded maps; writes results.csv
├── results.csv                # Output of benchmark.py
├── requirements.txt           # Python dependencies (pip install -r requirements.txt)
├── .gitignore                 # Ignores __pycache__ and compiled files
│
├── core/                      # Pure logic — no GUI dependency
│   ├── __init__.py
│   ├── grid.py                # Grid model, cell states, terrain cost, maze generation, neighbor queries
│   ├── heuristics.py          # Manhattan & Euclidean distance functions
│   ├── algorithms.py          # GBFS and A* as Python generators + instant-solve variant
│   ├── agent.py               # Moving agent: path following, trail tracking, re-planning
│   └── search_result.py       # SearchResult dataclass (path, metrics, visited nodes)
│
├── gui/                       # Presentation layer — rendering and controls only
│   ├── __init__.py
│   ├── app.py                 # Main app: state machine, event loop, sidebar layout
│   ├── renderer.py            # Grid drawing, rough-terrain tint, agent glow, obstacle flash, replan overlay
│   ├── controls.py            # Reusable widgets: Button, ToggleGroup, Slider, MetricCard
│   └── theme.py               # Design tokens: all colors, sizes, animation constants
│
├── tests/                     # Unit tests
│   ├── __init__.py
│   └── test_weighted.py       # Terrain-cost tests for A* and GBFS
│
├── docs/                      # Screenshots from the running application
│
└── README.md                  # This file
```

---

## How to Use

### Static Search Mode

1. Set your **grid size** using the Rows and Cols sliders
2. Select an **algorithm** — GBFS or A*
3. Select a **heuristic** — Manhattan or Euclidean
4. Optionally click **Generate Maze** to fill the grid with random obstacles,
   or click and drag directly on the grid to paint walls manually
5. Optionally **right-click** cells to mark them as rough terrain (orange, cost 5)
6. Adjust **Viz Speed** to control how fast the animation plays
7. Click **Run Search** or press `R` — watch the frontier expand in amber,
   visited cells fill in indigo-blue, and the final path light up in mint green

### Dynamic Mode

1. Configure the grid, terrain and algorithm as above
2. Set **Spawn %** to control how often new obstacles appear per step
3. Set **Agent Spd** to control how fast the agent moves
4. Click **Dynamic Mode** or press `D`
5. The agent computes an initial path and begins moving
6. When a new obstacle spawns on the agent's route, re-planning fires automatically —
   you will see a cyan sweep for the re-search expansion and a gold flash for the new path
7. The trail of already-walked cells turns violet with a depth-fade effect

### Editing the Map

- **Left-click** on any empty cell to place a wall
- **Left-click** on any wall to remove it
- **Click and drag** to paint or erase multiple cells in one stroke
- **Right-click** on any empty cell to make it rough terrain (cost 5); right-click again to make it normal (cost 1)
- The start and goal nodes cannot be overwritten
- **Clear Grid** (or `C`) removes walls and resets all terrain to normal

---

## Terrain Costs

Every cell has a traversal cost. The cost is paid when the agent **enters** the cell.

| Terrain | Cost | How to place |
|---|---|---|
| Normal | 1 | Default |
| Rough | 5 | Right-click an empty cell (shown in orange) |
| Wall | Blocked | Left-click |

The **path cost** is the sum of the costs of every cell entered after the start cell.
On a grid with only normal cells it equals the number of moves, so behaviour on plain maps
is unchanged. On rough terrain the cheapest route can be longer than the shortest one.

The cost values are a proxy for energy, not a calibrated model of battery or motor physics.

---

## Algorithms

### Greedy Best-First Search (GBFS)

```
f(n) = h(n)
```

GBFS expands whichever node appears closest to the goal according to the heuristic alone.
It ignores how expensive the path to the current node already is, so it does not avoid rough terrain.
The cost it reports is still the true weighted cost of the path it found.

- **Fast** — reaches the goal with few expansions in open environments
- **Not optimal** — may return a longer or more expensive path than necessary
- **Susceptible to heuristic traps** — can get stuck chasing dead ends in dense mazes

### A* Search

```
f(n) = g(n) + h(n)
g(n) = g(parent) + Cost(n)
```

A* balances the actual cost from the start `g(n)` with the estimated cost to the goal `h(n)`.
`g(n)` accumulates the terrain cost of every cell entered.

- **Optimal** — guaranteed to find the cheapest path with an admissible heuristic
- **Complete** — will always find a path if one exists
- **Slower than GBFS** (more nodes expanded), but far more reliable on complex or rough maps

---

## Heuristics

| Heuristic | Formula | Notes |
|---|---|---|
| **Manhattan** | `\|r1-r2\| + \|c1-c2\|` | Ideal for 4-directional grids — tight lower bound, always admissible |
| **Euclidean** | `sqrt((r1-r2)^2 + (c1-c2)^2)` | Straight-line distance — admissible but weaker bound, explores more nodes |

Both heuristics stay admissible with terrain costs because the minimum cost of entering a
cell is 1. If a minimum cost below 1 were ever introduced, the heuristic would have to be
scaled by that minimum.

Manhattan is the recommended choice for this grid environment.
Euclidean is provided for comparison and experimentation.

---

## Dynamic Mode

When **Dynamic Mode** is active, the following happens each agent step:

1. With probability **Spawn %**, a new wall is placed on a random empty cell
2. The agent checks whether the new wall intersects its **remaining planned path**
   - If **no intersection** — agent continues without any re-planning (O(1) check)
   - If **intersection detected** — full re-plan is triggered instantly from the agent's current position,
     using the same terrain costs
3. The agent moves one step forward along its current path
4. Visual overlays show:
   - **Orange-red flash** on the new wall (fades over 0.55 s)
   - **Cyan sweep** of nodes explored during re-planning
   - **Gold flash** on the newly computed path (fades over 1.2 s)
   - **Violet trail** of cells the agent has already walked through

The re-plan counter, obstacle-hit count, and step count are all tracked in the metrics sidebar.

---

## Metrics

| Card | Meaning |
|---|---|
| **NODES** | Nodes expanded by the search |
| **PATH COST** | Weighted cost of the planned path. In dynamic mode it is the cost of the latest plan from the point where the agent replanned |
| **TIME (ms)** | Search time. In the animated static search this includes the animation delay, so use `benchmark.py` for algorithm timing |
| **REPLANS** | Number of re-plans triggered by new obstacles |
| **STEPS** | Moves taken by the agent |
| **OBS HIT** | New obstacles that landed on the agent's remaining path |

---

## Visual Legend

| Color | Element | Meaning |
|---|---|---|
| Teal | Start node | Fixed starting position |
| Rose / Pink | Goal node | Pulsing destination — fixed target |
| Amber / Yellow | Frontier | Nodes currently in the open list (priority queue) |
| Indigo Blue | Visited | Nodes that have been fully expanded (closed list) |
| Mint Green | Path | The computed solution path |
| Orange / Brown | Rough terrain | Cells with cost 5; added by right-click |
| Violet | Trail | Cells the agent has already walked through (dynamic mode) |
| Bright Yellow | Agent | Current agent position — pulsing glow dot |
| Bright Cyan | Replan visited | Nodes explored during a re-planning event |
| Gold | Replan path | The newly computed path after an obstacle blocks the route |
| Dark | Wall | Impassable obstacle cell |

---

## Keyboard and Mouse Controls

| Input | Action |
|---|---|
| `R` | Run Search |
| `D` | Start Dynamic Mode |
| `G` | Generate random maze |
| `C` | Clear grid (walls and terrain) |
| `ESC` | Stop current run |
| Left-click on grid | Place or remove a wall |
| Left-click and drag | Paint or erase walls continuously |
| Right-click on grid | Toggle rough terrain (cost 5 / cost 1) |

Map editing is available when no search or dynamic run is in progress.

---

## Configuration

All settings are adjustable via the sidebar sliders at runtime — no config files needed.

| Setting | Range | Description |
|---|---|---|
| Rows | 5 – 40 | Grid height in cells |
| Cols | 5 – 60 | Grid width in cells |
| Density | 5% – 65% | Obstacle coverage for random maze generation |
| Viz Speed | 1x – 10x | How fast the search animation plays |
| Spawn % | 1% – 40% | Probability of a new obstacle spawning each agent step |
| Agent Spd | 1x – 8x | How fast the agent moves along its path |

---

## Testing

Run the unit tests from the project folder:

```bash
python -m unittest tests.test_weighted -v
```

The three tests check that:

1. A* takes a longer route when it is cheaper (5 moves, cost 5) than crossing two rough cells
2. GBFS walks straight through the rough cells (3 moves, cost 11)
3. On a grid without rough terrain the path cost equals the number of moves

---

## Benchmark and Results

`benchmark.py` runs A* and GBFS with both heuristics on 10 fixed, seeded 20x20 maps
(20% walls, 25% rough cells of cost 5) and saves every run to `results.csv`:

```bash
python benchmark.py
```

Average results over the 10 maps:

| Algorithm | Heuristic | Avg path cost | Avg path length | Avg nodes expanded |
|---|---|---|---|---|
| A* | Manhattan | 45.2 | 36.8 | 182.7 |
| A* | Euclidean | 45.2 | 36.8 | 214.9 |
| GBFS | Manhattan | 79.2 | 39.2 | 43.9 |
| GBFS | Euclidean | 74.2 | 36.6 | 42.7 |

A* paths cost about 43% less than GBFS (Manhattan), but A* expands about 4x more nodes.
Costs, lengths and node counts are repeatable; times depend on the machine.

---

## Screenshots

Screenshots from the running application are stored in the [`docs/`](docs/) folder:
the grid editor with rough terrain, a finished A* search, and dynamic mode after a re-plan.

---

## Future Work

- Dijkstra baseline for a cost-optimal comparison
- Calibrated energy values instead of the cost proxy
- More terrain types

---

## Team

| Name | ID | Area |
|---|---|---|
| Utkarsh | 2024UIT3016 | Algorithm development |
| Dilshad | 2024UIT3037 | Grid and terrain model |
| Shivam Poojan Yadav | 2024UIT3015 | Integration and GitHub |
| Saurabh | 2024UIT3049 | GUI and simulation |
| Sahil Aggarwal | 2024UIT3026 | Implementation and testing |
| Sohaib | 2024UIT3066 | Experiments and benchmarking |

B.Tech Information Technology, NSUT.
