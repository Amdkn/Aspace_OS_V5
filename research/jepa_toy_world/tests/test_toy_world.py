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


class RendererAndEnvironmentTests(unittest.TestCase):
    def test_renderer_contract_and_repeatability(self):
        layout = generate_layout(42)
        state = initial_state(layout, 42)
        frame_a = render_rgb(state, layout)
        frame_b = render_rgb(state, layout)
        self.assertEqual((frame_a.width, frame_a.height, frame_a.channels), (192,192,3))
        self.assertEqual(len(frame_a.pixels), 192*192*3)
        self.assertEqual(frame_a.pixels, frame_b.pixels)
        self.assertEqual(hashlib.sha256(frame_a.pixels).hexdigest(), hashlib.sha256(frame_b.pixels).hexdigest())

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
