"""Host-side frame parser (EEG-plan.md, B4). Reads raw bytes from stdin and
decodes them with framing.py — the same logic firmware's usbTxTask will use.

For now stdin is fed by simulator.py; once hardware exists this can be
pointed at a pyserial connection to the USB CDC port instead.
"""

import sys

from framing import LSB_VOLTS, find_and_decode


def main() -> None:
    buf = bytearray()
    frame_count = 0
    stdin = sys.stdin.buffer
    while True:
        chunk = stdin.read(4096)
        if not chunk:
            break
        buf += chunk
        while True:
            samples, buf = find_and_decode(buf)
            if samples is None:
                break
            frame_count += 1
            volts = [s * LSB_VOLTS for s in samples]
            uv = [v * 1e6 for v in volts]
            print(f"frame {frame_count}: " + " ".join(f"{v:+7.2f}uV" for v in uv))

    print(f"\n{frame_count} frames decoded, {len(buf)} trailing bytes unparsed", file=sys.stderr)


if __name__ == "__main__":
    main()
