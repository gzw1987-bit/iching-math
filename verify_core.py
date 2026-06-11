#!/usr/bin/env python3
"""No-dependency verification of the core King Wen permutation claims."""

from math import gcd

HEXAGRAM_MAP = {
    "111111": 1, "000000": 2, "100010": 3, "010001": 4,
    "111010": 5, "010111": 6, "010000": 7, "000010": 8,
    "111011": 9, "110111": 10, "111000": 11, "000111": 12,
    "101111": 13, "111101": 14, "001000": 15, "000100": 16,
    "100110": 17, "011001": 18, "110000": 19, "000011": 20,
    "100101": 21, "101001": 22, "000001": 23, "100000": 24,
    "100111": 25, "111001": 26, "100001": 27, "011110": 28,
    "010010": 29, "101101": 30, "001110": 31, "011100": 32,
    "001111": 33, "111100": 34, "000101": 35, "101000": 36,
    "101011": 37, "110101": 38, "001010": 39, "010100": 40,
    "110001": 41, "100011": 42, "111110": 43, "011111": 44,
    "000110": 45, "011000": 46, "010110": 47, "011010": 48,
    "101110": 49, "011101": 50, "100100": 51, "001001": 52,
    "001011": 53, "110100": 54, "101100": 55, "001101": 56,
    "011011": 57, "110110": 58, "010011": 59, "110010": 60,
    "110011": 61, "001100": 62, "101010": 63, "010101": 64,
}

KING_WEN_FROM_BINARY = [
    2, 23, 8, 20, 16, 35, 45, 12,
    15, 52, 39, 53, 62, 56, 31, 33,
    7, 4, 29, 59, 40, 64, 47, 6,
    46, 18, 48, 57, 32, 50, 28, 44,
    24, 27, 3, 42, 51, 21, 17, 25,
    36, 22, 63, 37, 55, 30, 49, 13,
    19, 41, 60, 61, 54, 38, 58, 10,
    11, 26, 5, 9, 34, 14, 43, 1,
]


def lcm(a, b):
    return a * b // gcd(a, b)


def decompose(perm):
    visited = [False] * len(perm)
    cycles = []
    for i in range(len(perm)):
        if visited[i]:
            continue
        cycle = []
        j = i
        while not visited[j]:
            visited[j] = True
            cycle.append(j)
            j = perm[j]
        cycles.append(cycle)
    return sorted(cycles, key=len, reverse=True)


def hamming(a, b):
    return sum(x != y for x, y in zip(a, b))


def check(name, observed, expected):
    if observed != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {observed!r}")
    print(f"ok {name}: {observed}")


def main():
    check("HEXAGRAM_MAP key count", len(HEXAGRAM_MAP), 64)
    check("HEXAGRAM_MAP unique values", len(set(HEXAGRAM_MAP.values())), 64)
    check(
        "HEXAGRAM_MAP six-bit keys",
        all(len(k) == 6 and set(k) <= {"0", "1"} for k in HEXAGRAM_MAP),
        True,
    )

    perm = [n - 1 for n in KING_WEN_FROM_BINARY]
    cycles = decompose(perm)
    lengths = [len(cycle) for cycle in cycles]
    fixed_points = sum(1 for cycle in cycles if len(cycle) == 1)
    order = 1
    for length in lengths:
        order = lcm(order, length)

    check("cycle lengths", lengths, [52, 10, 2])
    check("fixed points", fixed_points, 0)
    check("order", order, 260)

    binary_by_wen = {wen: bits for bits, wen in HEXAGRAM_MAP.items()}
    distances = [
        hamming(binary_by_wen[wen], binary_by_wen[wen + 1])
        for wen in range(1, 64)
    ]
    distribution = [distances.count(i) for i in range(7)]
    mean = sum(distances) / len(distances)
    even = sum(1 for distance in distances if distance % 2 == 0)
    odd = len(distances) - even

    check("Hamming distribution d=0..6", distribution, [0, 2, 20, 13, 19, 0, 9])
    check("mean Hamming distance rounded", round(mean, 3), 3.349)
    check("even:odd adjacent Hamming steps", (even, odd), (48, 15))


if __name__ == "__main__":
    main()
