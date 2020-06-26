import unittest
from unittest.mock import patch
from main import main, _get_input


class MainTest(unittest.TestCase):
    @patch("main._get_input")
    def test_main(self, input_mock):
        input_mock.side_effect = [
            (0, ["(S& W)>E", "(W&P)>H", "R>!H", "R>G", "W", "R", "S"], "E"),
            (0, ["M>I", "!M>A", "(I|A)>H"], "!H"),
            (0, ["A>B", "!B", "!A>(C|D)", "C>E", "F>!E", "F"], "D"),
            (0, ["(P>Q)>Q", "(P>P)>R", "(R>S)>!(S>Q)"], "R"),
            (1, ["P|(Q&(R>T))", "P>R", "Q>T", "Q>(R=T)"], "R"),
        ]
        self.assertEqual(main(), 1)
        self.assertEqual(main(), 0)
        self.assertEqual(main(), 1)
        self.assertEqual(main(), 1)
        self.assertEqual(main(), 1)

    def test__get_input(self):
        user_input = [
            "7 0\r",
            "(S& W)>E\r",
            "(W&P)>H\r",
            "R>!H\r",
            "R>G\r",
            "W\r",
            "R\r",
            "S\r",
            "E\r",
        ]
        with patch("builtins.input", side_effect=user_input):
            self.assertEqual(
                _get_input(),
                (0, ["(S& W)>E", "(W&P)>H", "R>!H", "R>G", "W", "R", "S"], "E"),
            )
