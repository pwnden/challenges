"""Find the input that opens the rotor lock."""

import sys

TARGET = [
    9, 120, 219, 92, 215, 75, 200, 40, 243, 122, 236, 79, 113, 105, 40, 89,
    248, 106, 1, 204, 122, 216, 219, 142, 214, 101, 171, 35, 255, 109, 142, 176,
    5, 30,
]


def encode(value):
    previous = 0xA7
    result = []
    for index, byte in enumerate(value):
        mixed = byte ^ ((0x53 + 13 * index) & 0xFF) ^ previous
        shift = index % 7 + 1
        previous = ((mixed << shift) | (mixed >> (8 - shift))) & 0xFF
        result.append(previous)
    return result


def main():
    if len(sys.argv) != 2:
        print("usage: python3 checker.py <flag>", file=sys.stderr)
        return 2
    if encode(sys.argv[1].encode("utf-8")) == TARGET:
        print("unlocked")
        return 0
    print("locked", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
