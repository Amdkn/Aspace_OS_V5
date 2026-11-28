"""Pixel-space persistence baseline."""
from ..env.toy_world import RGBFrame


def predict(observation: RGBFrame, horizon: int = 1) -> RGBFrame:
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    # The unchanged-world prediction is the same image at every future horizon.
    return observation
