import unittest
from unittest.mock import patch
from main import main


class MainTest(unittest.TestCase):
    @patch('main._get_input')
    def test_main(self, input_mock):
        input_mock.side_effect = [
            (0, ['(S& W)>E', '(W&P)>H', 'R>!H', 'R>G', 'W', 'R', 'S'], 'E'),
            (0, ['M>I', '!M>A', '(I|A)>H'], '!H'),
            (0, ['A>B', '!B', '!A>(C|D)', 'C>E', 'F>!E', 'F'], 'D'),
            (0, ['(P>Q)>Q', '(P>P)>R', '(R>S)>!(S>Q)'], 'R'),
            (0, ['P|(Q&(R>T))', 'P>R', 'Q>T', 'Q>(R=T)'], 'R')
        ]
        self.assertEqual(main(), 1)
        self.assertEqual(main(), 0)
        self.assertEqual(main(), 1)
        self.assertEqual(main(), 1)
        self.assertEqual(main(), 1)
