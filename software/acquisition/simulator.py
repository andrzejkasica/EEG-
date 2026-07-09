"""Fakes ADS1299 acquisition + usbTxTask framing so receiver.py can be
validated end-to-end before any hardware exists (EEG-plan.md, B4).

Writes raw framed bytes to stdout — pipe into receiver.py:
    python3 simulator.py 200 | python3 receiver.py
"""

import math
import random
import sys

from framing import LSB_VOLTS, NUM_CHANNELS, encode_frame

FULL_SCALE_CODE = 2**23 - 1


def generate_sample_volts(t: float, channel: int) -> float:
    """Rough alpha-band-ish EEG signal (~20uV) plus noise, phase-offset per channel."""
    alpha = 20e-6 * math.sin(2 * math.pi * 10 * t + channel)
    noise = random.gauss(0, 5e-6)
    return alpha + noise


def frame_stream(num_frames: int, sample_rate_hz: float = 250.0):
    for n in range(num_frames):
        t = n / sample_rate_hz
        samples = []
        for ch in range(NUM_CHANNELS):
            volts = generate_sample_volts(t, ch)
            code = int(round(volts / LSB_VOLTS))
            code = max(-FULL_SCALE_CODE - 1, min(FULL_SCALE_CODE, code))
            samples.append(code)
        yield encode_frame(samples)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    out = sys.stdout.buffer
    for frame in frame_stream(n):
        out.write(frame)
    out.flush()
