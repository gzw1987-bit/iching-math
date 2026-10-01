import contextlib
import io
import sys
import types
import unittest
from unittest.mock import patch

import verify
from verify_core import HEXAGRAM_MAP, decompose, hamming


class VerificationTests(unittest.TestCase):
    def test_invalid_permutations_fail_instead_of_partial_cycles(self):
        for permutation in ([0, 0], [0, -1], [0, 2], [False], [0.0]):
            with self.subTest(permutation=permutation), self.assertRaises(ValueError):
                decompose(permutation)
        self.assertEqual(decompose([1, 2, 0]), [[0, 1, 2]])
        self.assertEqual(decompose([]), [])

    def test_hamming_rejects_truncated_input(self):
        with self.assertRaises(ValueError):
            hamming('110', '11')
        self.assertEqual(hamming('110', '101'), 2)

    def run_fixture(self, *, incomplete=False, empty=False, offline=False):
        names = {number: {'name': str(number)} for number in range(1, 65)}
        texts = {}
        pages = {}
        for binary, number in HEXAGRAM_MAP.items():
            keys = [verify.get_our_yao_key(pos, binary[pos - 1] == '1') for pos in range(1, 7)]
            if number == 1:
                keys.append('用九')
            if number == 2:
                keys.append('用六')
            our = {key: key + '，' + ('' if empty else 'fixture') for key in keys}
            if incomplete and number == 1:
                our.pop('用九')
            texts[number] = {'yaoci': our}
            pages[number] = ''.join('<td>' + key + '，fixture</td>' for key in keys)
        cast = types.ModuleType('cast_hexagram')
        cast.HEXAGRAM_MAP, cast.HEXAGRAMS = HEXAGRAM_MAP, names
        yaoci = types.ModuleType('yaoci_data')
        yaoci.YAOCI = texts
        with patch.dict(sys.modules, {'cast_hexagram': cast, 'yaoci_data': yaoci}), \
             patch.object(verify, 'fetch_page', side_effect=lambda number: None if offline else pages[number]), \
             patch.object(verify.time, 'sleep'), contextlib.redirect_stdout(io.StringIO()):
            return verify.main()

    def test_complete_386_line_fixture_passes(self):
        self.assertEqual(self.run_fixture(), 0)

    def test_missing_special_line_fails_completeness(self):
        self.assertEqual(self.run_fixture(incomplete=True), 1)

    def test_empty_text_cannot_match(self):
        self.assertEqual(self.run_fixture(empty=True), 1)

    def test_fetch_failure_is_a_nonzero_exit(self):
        self.assertEqual(self.run_fixture(offline=True), 1)
