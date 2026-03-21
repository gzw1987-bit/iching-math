#!/usr/bin/env python3
"""
Monte Carlo simulation: cycle structure of random permutations of 64 elements.
Compares against the observed King Wen permutation cycle type (52, 10, 2).
"""
import random

N = 64
TRIALS = 2_000_000
TARGET = (52, 10, 2)

def cycle_type(perm):
    """Return sorted cycle lengths (descending) of a permutation."""
    visited = [False] * len(perm)
    lengths = []
    for i in range(len(perm)):
        if visited[i]:
            continue
        length = 0
        j = i
        while not visited[j]:
            visited[j] = True
            j = perm[j]
            length += 1
        lengths.append(length)
    lengths.sort(reverse=True)
    return tuple(lengths)

def main():
    elements = list(range(N))

    exact_match = 0
    exactly_3_cycles = 0
    max_cycle_ge_52 = 0
    zero_fixed_points = 0

    print(f"Running {TRIALS:,} random permutations of {N} elements...")
    print()

    for trial in range(TRIALS):
        perm = elements[:]
        random.shuffle(perm)

        ct = cycle_type(perm)

        if ct == TARGET:
            exact_match += 1

        if len(ct) == 3:
            exactly_3_cycles += 1

        if ct[0] >= 52:
            max_cycle_ge_52 += 1

        # Count fixed points
        fp = sum(1 for i in range(N) if perm[i] == i)
        if fp == 0:
            zero_fixed_points += 1

        if (trial + 1) % 500_000 == 0:
            print(f"  ...{trial + 1:,} done")

    print()
    print("=" * 60)
    print("Results")
    print("=" * 60)
    print(f"  Trials:                        {TRIALS:,}")
    print(f"  Exact match (52,10,2):         {exact_match:,}  ({exact_match/TRIALS*100:.4f}%)")
    print(f"  Exactly 3 cycles:              {exactly_3_cycles:,}  ({exactly_3_cycles/TRIALS*100:.2f}%)")
    print(f"  Max cycle >= 52:               {max_cycle_ge_52:,}  ({max_cycle_ge_52/TRIALS*100:.2f}%)")
    print(f"  Zero fixed points:             {zero_fixed_points:,}  ({zero_fixed_points/TRIALS*100:.2f}%)")
    print()

    # Theoretical probability of exact cycle type (52,10,2)
    # For a permutation of n elements, the probability of cycle type (c1,c2,...,ck)
    # where all ci are distinct is: n! / (c1 * c2 * ... * ck * n!)
    # Wait -- the exact formula:
    # P = 1 / (c1 * c2 * ... * ck) when all cycle lengths are distinct
    # This is because the number of permutations with cycle type (c1,c2,...,ck)
    # (all distinct) is n! / (c1 * c2 * ... * ck), so the probability is
    # 1 / (c1 * c2 * ... * ck).
    theoretical = 1.0 / (52 * 10 * 2)
    print(f"  Theoretical probability:       1/(52*10*2) = 1/{52*10*2} = {theoretical*100:.4f}%")
    print(f"  Theoretical expected count:    {theoretical * TRIALS:.1f}")
    print()

if __name__ == "__main__":
    main()
