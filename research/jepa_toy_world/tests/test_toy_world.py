from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from research.jepa_toy_world.env.toy_world import (
    PCG32, ToyWorldEnv, canonical_json, generate_layout, initial_state,
    sha256_id, transition_state
)
from research.jepa_toy_world.env.renderer import render_rgb
from research.jepa_toy_world.baselines.persistence import predict as persistence_predict
from research.jepa_toy_world.baselines.symbolic_oracle import predict as symbolic_predict
from research.jepa_toy_world.evaluator.baseline_smoke import run_smoke


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "spec" / "transition-fixtures.v1.json"


class PCG32Tests(unittest.TestCase):
    def test_known_answer_vectors(self):
        expected = {
            0: [3894649422,2055130073,2315086854,2925816488,3443325253,1644475139,428639621,1241310737,3521718650,338531392],
            1: [1412771199,1791099446,124312908,1968572995,1080415314,2578637408,2103691749,1218125110,776621019,4155847760],
            42: [3270867926,1795671209,1924641435,1143034755,4121910957,1757328946,3418829100,3589261271,2062288904,4279450293],
        }
        for seed, vector in expected.items():
            rng = PCG32(seed)
            self.assertEqual([rng.next_u32() for _ in range(10)], vector)

    def test_randbelow_rejection_sampling(self):
        rng = PCG32(0)
        draws = iter([0, 5])
        rng.next_u32 = lambda: next(draws)
        self.assertEqual(rng.randbelow(3), 2)

    def test_seed_validation(self):
        for seed in (-1, 1 << 64, True, 1.5):
            with self.assertRaises(ValueError):
                PCG32(seed)

    def test_seed_selects_reproducible_layout(self):
        self.assertEqual(generate_layout(42), generate_layout(42))
        self.assertEqual(generate_layout(42)["layout_id"], generate_layout(42)["layout_id"])


class TransitionTests(unittest.TestCase):
    def test_hand_authored_fixtures(self):
        payload = json.loads(FIXTURES.read_text(encoding="utf-8"))
        for fixture in payload["fixtures"]:
            with self.subTest(fixture=fixture["id"]):
                layout = fixture["layout"]
                state = initial_state(layout, 0)
                state.update(fixture["before"])
                result = transition_state(state, layout, fixture["action"])
                for key in ("tick","agent","crates","gates","plates","goal","terminal"):
                    self.assertEqual(result[key], fixture["after"][key], key)

    def test_transition_is_pure_and_deterministic(self):
        layout = generate_layout(42)
        state = initial_state(layout, 42)
        original = json.loads(canonical_json(state))
        first = transition_state(state, layout, "NOOP")
        second = transition_state(state, layout, "NOOP")
        self.assertEqual(first, second)
        self.assertEqual(state, original)

    def test_unknown_action_is_rejected_without_mutation(self):
        layout = generate_layout(7)
        state = initial_state(layout, 7)
        before = json.loads(canonical_json(state))
        with self.assertRaises(ValueError):
            transition_state(state, layout, "FLY")
        self.assertEqual(state, before)

    def test_closed_manual_gate_blocks_agent(self):
        layout = {
            "schema_version":"toy-world.layout.v1","layout_id":"closed-gate","width":12,"height":12,
            "walls":[],"agent_spawn":{"x":2,"y":2,"facing":"E"},"crates":[],
            "gates":[{"id":"gate-01","x":3,"y":2,"mode":"manual","initial_open":False}],
            "plates":[],"goal":{"x":9,"y":9}
        }
        state=initial_state(layout,0)
        result=transition_state(state,layout,"MOVE_E")
        self.assertEqual((result["agent"]["x"],result["agent"]["y"]),(2,2))
        self.assertEqual(result["agent"]["facing"],"E")
        self.assertEqual(result["tick"],1)

    def test_push_is_blocked_by_second_crate(self):
        layout = {
            "schema_version":"toy-world.layout.v1","layout_id":"double-crate","width":12,"height":12,
            "walls":[],"agent_spawn":{"x":2,"y":3,"facing":"E"},
            "crates":[{"id":"crate-01","x":3,"y":3},{"id":"crate-02","x":4,"y":3}],
            "gates":[],"plates":[],"goal":{"x":9,"y":9}
        }
        state=initial_state(layout,0)
        result=transition_state(state,layout,"MOVE_E")
        self.assertEqual(result["agent"],state["agent"])
        self.assertEqual(result["crates"],state["crates"])

    def test_pressure_gate_closes_when_plate_is_released(self):
        layout = {
            "schema_version":"toy-world.layout.v1","layout_id":"pressure-release","width":12,"height":12,
            "walls":[],"agent_spawn":{"x":2,"y":2,"facing":"E"},"crates":[],
            "gates":[{"id":"gate-01","x":6,"y":2,"mode":"pressure","initial_open":False}],
            "plates":[{"id":"plate-01","x":3,"y":2,"controls_gate_id":"gate-01"}],"goal":{"x":9,"y":9}
        }
        state=initial_state(layout,0)
        on_plate=transition_state(state,layout,"MOVE_E")
        self.assertTrue(on_plate["gates"][0]["open"])
        off_plate=transition_state(on_plate,layout,"MOVE_W")
        self.assertFalse(off_plate["gates"][0]["open"])
        self.assertFalse(off_plate["plates"][0]["active"])

    def test_terminal_state_rejects_additional_actions(self):
        layout = {
            "schema_version":"toy-world.layout.v1","layout_id":"terminal","width":12,"height":12,
            "walls":[],"agent_spawn":{"x":4,"y":5,"facing":"E"},"crates":[],
            "gates":[],"plates":[],"goal":{"x":5,"y":5}
        }
        state=initial_state(layout,0)
        terminal=transition_state(state,layout,"MOVE_E")
        self.assertTrue(terminal["terminal"])
        with self.assertRaises(ValueError):
            transition_state(terminal,layout,"NOOP")

    def test_oracle_matches_direct_transition(self):
        layout = generate_layout(17)
        state = initial_state(layout, 17)
        actions = ["MOVE_E", "NOOP", "MOVE_S"]
        expected = state
        for action in actions:
            expected = transition_state(expected, layout, action)
        self.assertEqual(symbolic_predict(state, layout, actions), expected)

    def test_layout_and_state_hashes_are_stable(self):
        layout_a = generate_layout(123)
        layout_b = generate_layout(123)
        self.assertEqual(sha256_id(layout_a), sha256_id(layout_b))
        self.assertEqual(sha256_id(initial_state(layout_a, 123)), sha256_id(initial_state(layout_b, 123)))

    def test_layout_hash_ignores_nonsemantic_array_order(self):
        from copy import deepcopy
        from research.jepa_toy_world.env.toy_world import canonical_layout
        layout_a = generate_layout(42)
        layout_b = deepcopy(layout_a)
        layout_b["walls"] = list(reversed(layout_b["walls"]))
        layout_b["crates"] = list(reversed(layout_b["crates"]))
        layout_b["gates"] = list(reversed(layout_b["gates"]))
        layout_b["plates"] = list(reversed(layout_b["plates"]))
        self.assertEqual(sha256_id(canonical_layout(layout_a)), sha256_id(canonical_layout(layout_b)))


class RendererAndEnvironmentTests(unittest.TestCase):
    def test_baseline_smoke_oracle_is_exact(self):
        report=run_smoke()
        self.assertEqual(report["episodes"],4)
        self.assertEqual(report["evaluations"],16)
        self.assertEqual(report["oracle_state_exact_rate"],1.0)
        self.assertEqual(report["oracle_pixel_exact_rate"],1.0)

    def test_renderer_contract_and_repeatability(self):
        layout = generate_layout(42)
        state = initial_state(layout, 42)
        frame_a = render_rgb(state, layout)
        frame_b = render_rgb(state, layout)
        self.assertEqual((frame_a.width, frame_a.height, frame_a.channels), (192,192,3))
        self.assertEqual(len(frame_a.pixels), 192*192*3)
        self.assertEqual(frame_a.pixels, frame_b.pixels)
        self.assertEqual(hashlib.sha256(frame_a.pixels).hexdigest(), hashlib.sha256(frame_b.pixels).hexdigest())
        self.assertEqual(hashlib.sha256(frame_a.pixels).hexdigest(), "84d27dff64030f19d0fd2739b17f4bbf390bc88821c92a85f3853481f8a48564")

    def test_persistence_baseline_returns_same_frame(self):
        env = ToyWorldEnv()
        frame, _ = env.reset(seed=42)
        self.assertIs(persistence_predict(frame, 5), frame)

    def test_candidate_interface_does_not_return_ground_truth(self):
        env = ToyWorldEnv()
        observation, info = env.reset(seed=42)
        self.assertEqual(info, {})
        self.assertFalse(isinstance(observation, dict))
        next_observation, reward, terminated, truncated, step_info = env.step("NOOP")
        self.assertEqual(step_info, {})
        self.assertEqual((reward, terminated, truncated), (0.0, False, False))
        self.assertEqual(len(next_observation.pixels), 192*192*3)


if __name__ == "__main__":
    unittest.main()
