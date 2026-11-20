#!/usr/bin/env python3
"""No-dependency verification of the King Wen pair structure (非覆即变).

Scope and framing
-----------------
The pairing rule itself ("adjacent hexagrams 2k-1, 2k are related by
reversal 覆/综, or — when reversal is a fixed point — by complement
变/错") is a classical observation documented since antiquity. This
script does NOT claim it as a discovery. What it adds:

1. A machine-checkable proof that the rule holds with zero exceptions
   across all 32 pairs, pinned as regression values.
2. Quantitative observations that only become visible when computed:
   - exactly 4 pairs are BOTH reversal and complement pairs
     (泰否 11/12, 随蛊 17/18, 渐归妹 53/54, 既济未济 63/64);
   - nuclear-hexagram (互卦) iteration converges for all 64 hexagrams
     to the set {1 乾, 2 坤, 63 既济, 64 未济}, with fixed points
     exactly {1, 2} and the 2-cycle {63, 64};
   - interaction between the pairing and the [52, 10, 2] cycle
     decomposition: 24 of 32 pairs fall inside a single cycle; the
     10-cycle and 2-cycle memberships are pinned below.
3. A seeded random baseline for how often a random arrangement would
   satisfy the pairing rule on all 32 adjacent pairs.

These are structural facts about the sequence, not claims about why the
sequence was designed that way.
"""

import random

from verify_core import HEXAGRAM_MAP, KING_WEN_FROM_BINARY, check, decompose

NUM_TO_BINARY = {v: k for k, v in HEXAGRAM_MAP.items()}

# Pinned regression values (computed 2026-07-14, reproducible below).
EXPECTED_SELF_REVERSAL = [1, 2, 27, 28, 29, 30, 61, 62]
EXPECTED_PURE_COMPLEMENT_PAIRS = [(1, 2), (27, 28), (29, 30), (61, 62)]
EXPECTED_DOUBLE_PAIRS = [(11, 12), (17, 18), (53, 54), (63, 64)]
EXPECTED_NUCLEAR_FIXED_POINTS = [1, 2]
EXPECTED_NUCLEAR_TERMINAL_SET = [1, 2, 63, 64]
EXPECTED_TEN_CYCLE_MEMBERS = [10, 13, 14, 27, 34, 48, 52, 56, 61, 62]
EXPECTED_TWO_CYCLE_MEMBERS = [43, 63]
EXPECTED_SAME_CYCLE_PAIRS = 24


def reversal(binary: str) -> str:
    """综卦/覆: read the six lines bottom-to-top reversed."""
    return binary[::-1]


def complement(binary: str) -> str:
    """错卦/变: flip every line yin<->yang."""
    return "".join("1" if c == "0" else "0" for c in binary)


def nuclear(binary: str) -> str:
    """互卦: lines 2,3,4 as the lower trigram, lines 3,4,5 as the upper."""
    return binary[1:4] + binary[2:5]


def classify_pairs():
    pure_fu, pure_bian, both, neither = [], [], [], []
    for k in range(1, 33):
        a, b = 2 * k - 1, 2 * k
        ba, bb = NUM_TO_BINARY[a], NUM_TO_BINARY[b]
        is_fu = reversal(ba) == bb
        is_bian = complement(ba) == bb
        if is_fu and is_bian:
            both.append((a, b))
        elif is_fu:
            pure_fu.append((a, b))
        elif is_bian:
            pure_bian.append((a, b))
        else:
            neither.append((a, b))
    return pure_fu, pure_bian, both, neither


def nuclear_terminals():
    nuc = {n: HEXAGRAM_MAP[nuclear(NUM_TO_BINARY[n])] for n in range(1, 65)}
    fixed = sorted(n for n in nuc if nuc[n] == n)
    terminals = set()
    for n in range(1, 65):
        seen = []
        cur = n
        while cur not in seen:
            seen.append(cur)
            cur = nuc[cur]
        terminals.add(cur)
    return fixed, sorted(terminals)


def cycle_pair_interaction():
    perm = [n - 1 for n in KING_WEN_FROM_BINARY]
    cycles = decompose(perm)
    index_to_cycle = {}
    for ci, cyc in enumerate(cycles):
        for i in cyc:
            index_to_cycle[i] = ci
    num_to_index = {HEXAGRAM_MAP[b]: int(b, 2) for b in HEXAGRAM_MAP}
    same = sum(
        1
        for k in range(1, 33)
        if index_to_cycle[num_to_index[2 * k - 1]]
        == index_to_cycle[num_to_index[2 * k]]
    )
    by_len = {len(c): sorted(KING_WEN_FROM_BINARY[i] for i in c) for c in cycles}
    return same, by_len


def random_baseline(trials: int = 20000, seed: int = 20260714) -> float:
    """Fraction of random orderings whose 32 adjacent pairs ALL satisfy
    reversal-or-complement. Expected to be (numerically) zero; reported
    as an upper bound, not as evidence of intent."""
    rng = random.Random(seed)
    binaries = list(HEXAGRAM_MAP)
    hits = 0
    for _ in range(trials):
        rng.shuffle(binaries)
        ok = True
        for k in range(32):
            a, b = binaries[2 * k], binaries[2 * k + 1]
            if reversal(a) != b and complement(a) != b:
                ok = False
                break
        if ok:
            hits += 1
    return hits / trials


def main() -> int:

    # Involution sanity: both maps are involutions and they commute.
    for b in HEXAGRAM_MAP:
        assert reversal(reversal(b)) == b
        assert complement(complement(b)) == b
        assert reversal(complement(b)) == complement(reversal(b))
    print("ok involution + commutation for reversal/complement on all 64")

    self_rev = sorted(n for n in range(1, 65) if reversal(NUM_TO_BINARY[n]) == NUM_TO_BINARY[n])
    check("self-reversal hexagrams", self_rev, EXPECTED_SELF_REVERSAL)

    pure_fu, pure_bian, both, neither = classify_pairs()
    check("pure reversal pairs", len(pure_fu), 24)
    check("pure complement pairs", pure_bian, EXPECTED_PURE_COMPLEMENT_PAIRS)
    check("double (reversal AND complement) pairs", both, EXPECTED_DOUBLE_PAIRS)
    check("pairs violating 非覆即变", neither, [])

    fixed, terminals = nuclear_terminals()
    check("nuclear fixed points", fixed, EXPECTED_NUCLEAR_FIXED_POINTS)
    check("nuclear iteration terminal set", terminals, EXPECTED_NUCLEAR_TERMINAL_SET)

    same, by_len = cycle_pair_interaction()
    check("pairs inside a single cycle", same, EXPECTED_SAME_CYCLE_PAIRS)
    check("10-cycle King Wen members", by_len.get(10, []), EXPECTED_TEN_CYCLE_MEMBERS)
    check("2-cycle King Wen members", by_len.get(2, []), EXPECTED_TWO_CYCLE_MEMBERS)

    rate = random_baseline()
    print(f"ok random baseline: {rate:.6f} of 20000 seeded shuffles satisfy all 32 pairs")
    if rate > 0:
        print("   note: nonzero baseline would weaken nothing above; facts are exact, not statistical")

    print("\nall pair-structure checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
