import unittest
from core.grid import Grid
from core.agent import Agent
from core.heuristics import HeuristicType as H


class TestCostAwareReplanning(unittest.TestCase):
    def test_replan_after_new_obstacle_stays_cost_aware(self):
        g = Grid(5, 8)                      # start (1,1), goal (3,6)
        for c in range(2, 6):
            g.set_cost(2, c, 5)             # rough band on row 2
        agent = Agent(g, "ASTAR", H.MANHATTAN)
        first = agent.compute_initial_path()
        self.assertTrue(first.success)

        blocked = first.path[3]             # block a cell ahead on the path
        g.set_wall(*blocked, True)
        event = agent.check_and_replan(blocked)

        self.assertIsNotNone(event)
        self.assertEqual(agent.replanning_count, 1)
        self.assertTrue(event.success)
        self.assertNotIn(blocked, event.new_path)
        self.assertEqual(event.new_path[-1], g.goal.pos)
        # the new route must not cross the rough band (cost 5 cells)
        crossed = [p for p in event.new_path[1:] if g.cost_of(p) > 1]
        self.assertEqual(crossed, [])


if __name__ == "__main__":
    unittest.main()
