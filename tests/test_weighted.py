import unittest
from core.grid import Grid
from core.algorithms import solve_instant
from core.heuristics import HeuristicType as H


def rough_grid():
    g = Grid(3, 6)
    g.set_cost(1, 2, 5)
    g.set_cost(1, 3, 5)
    return g


class TestWeighted(unittest.TestCase):
    def test_astar_takes_cheaper_longer_route(self):
        r = solve_instant(rough_grid(), "ASTAR", H.MANHATTAN)
        self.assertEqual(r.path_cost, 5.0)
        self.assertEqual(len(r.path) - 1, 5)

    def test_gbfs_walks_through_rough_terrain(self):
        r = solve_instant(rough_grid(), "GBFS", H.MANHATTAN)
        self.assertEqual(r.path_cost, 11.0)

    def test_uniform_grid_cost_equals_moves(self):
        r = solve_instant(Grid(7, 7), "ASTAR", H.MANHATTAN)
        self.assertEqual(r.path_cost, 8.0)


if __name__ == "__main__":
    unittest.main()