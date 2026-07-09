"""USB frame encode/decode logic — mirrors the packing firmware's usbTxTask
will do (see EEG-plan.md, B3/B4): header byte + channel count + N x 24-bit
signed samples, big-endian. Shared by simulator.py and receiver.py so the
host parser is validated against the exact same framing the firmware
will later implement in C.
"""

HEADER = 0xA5
NUM_CHANNELS = 8
BYTES_PER_SAMPLE = 3
FRAME_SIZE = 2 + NUM_CHANNELS * BYTES_PER_SAMPLE  # 26 bytes

# ADS1299 default config used to convert codes <-> volts (gain=24, VREF=4.5V)
GAIN = 24
VREF = 4.5
LSB_VOLTS = (2 * VREF) / (GAIN * 2**24)


def encode_frame(samples: list[int]) -> bytes:
    if len(samples) != NUM_CHANNELS:
        raise ValueError(f"expected {NUM_CHANNELS} samples, got {len(samples)}")
    out = bytearray([HEADER, NUM_CHANNELS])
    for s in samples:
        out += int(s).to_bytes(BYTES_PER_SAMPLE, byteorder="big", signed=True)
    return bytes(out)


def decode_frame(buf: bytes) -> list[int]:
    if len(buf) != FRAME_SIZE:
        raise ValueError(f"expected {FRAME_SIZE} bytes, got {len(buf)}")
    if buf[0] != HEADER:
        raise ValueError(f"bad header byte: {buf[0]:#x}")
    count = buf[1]
    if count != NUM_CHANNELS:
        raise ValueError(f"unexpected channel count: {count}")
    samples = []
    for i in range(count):
        chunk = buf[2 + i * BYTES_PER_SAMPLE : 2 + (i + 1) * BYTES_PER_SAMPLE]
        samples.append(int.from_bytes(chunk, byteorder="big", signed=True))
    return samples


def find_and_decode(stream: bytearray) -> tuple[list[int] | None, bytearray]:
    """Scan `stream` for one valid frame starting at HEADER.

    Returns (samples, remaining_bytes) if a frame was decoded, or
    (None, remaining_bytes) if more data is needed. Resyncs a byte at a
    time on a false-positive header match (a data byte that happens to
    equal HEADER) or a bad channel count.
    """
    while True:
        idx = stream.find(bytes([HEADER]))
        if idx == -1:
            return None, bytearray()
        if idx > 0:
            stream = stream[idx:]
        if len(stream) < FRAME_SIZE:
            return None, stream
        try:
            samples = decode_frame(bytes(stream[:FRAME_SIZE]))
            return samples, stream[FRAME_SIZE:]
        except ValueError:
            stream = stream[1:]
