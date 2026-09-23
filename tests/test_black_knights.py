import unittest

from black_knights import build_black_knights_agents


class BuildBlackKnightsAgentsTests(unittest.TestCase):
    def test_maps_active_blocked_and_idle_knights_to_3d_office_states(self):
        roster = {
            "Lelouch": {"role": "Lead / Orchestrator", "color": "#7c5cff"},
            "Rakshata": {"role": "Rust/Audio Engineer", "color": "#ff7a45"},
            "Kaguya": {"role": "Release Engineer", "color": "#c084fc"},
        }
        tasks = [
            {
                "id": "audio",
                "title": "Audio engine refresh",
                "status": "in_progress",
                "agents": [{"name": "Lelouch", "action": "Coordinating integration"}],
            },
            {
                "id": "release",
                "title": "Prepare the release",
                "status": "blocked",
                "agents": [{"name": "Rakshata", "action": "Waiting for device logs"}],
            },
        ]

        agents = {agent["name"]: agent for agent in build_black_knights_agents(roster, tasks)}

        self.assertEqual(agents["Lelouch"]["status"], "working")
        self.assertEqual(agents["Lelouch"]["home"], "meeting")
        self.assertIn("Audio engine refresh", agents["Lelouch"]["task"])
        self.assertEqual(agents["Rakshata"]["status"], "away")
        self.assertIn("Blocked", agents["Rakshata"]["task"])
        self.assertEqual(agents["Kaguya"]["status"], "idle")
        self.assertTrue(agents["Kaguya"]["home"].startswith("coffee"))
        self.assertEqual(agents["Kaguya"]["task"], "Coffee break — no assigned task")

    def test_reports_assignment_progress_from_the_same_task_feed(self):
        roster = {"Kallen": {"role": "Frontend Engineer", "color": "#ff3d5a"}}
        tasks = [
            {
                "id": "ui",
                "title": "Polish the dashboard",
                "status": "in_progress",
                "agents": [
                    {"name": "Kallen", "action": "Implementing interaction"},
                    {"name": "C.C.", "action": "Testing", "status": "done"},
                ],
            }
        ]

        agent = build_black_knights_agents(roster, tasks)[0]

        self.assertEqual(agent["stats"]["active"], 1)
        self.assertEqual(agent["stats"]["tasksDone"], 0)
        self.assertIn("1 active assignment", agent["output"])
        self.assertTrue(agent["typing"])


if __name__ == "__main__":
    unittest.main()
