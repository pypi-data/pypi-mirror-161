from unittest import main, TestCase
from unittest.mock import patch
from baraldi_fib_py.fib_calcs.fib_numbers import calc_nums


class Test(TestCase):
    @patch("baraldi_fib_py.fib_calcs.fib_numbers.recurring_fib_num")
    def test_calc_nums(self, mock_fib_calc):
        expected_outcome = [mock_fib_calc.return_value, mock_fib_calc.return_value]
        self.assertEqual(expected_outcome, calc_nums(nums=[3, 4]))
        self.assertEqual(2, len(mock_fib_calc.call_args_list))
        self.assertEqual({"num": 3}, mock_fib_calc.call_args_list[0][1])
        self.assertEqual({"num": 4}, mock_fib_calc.call_args_list[1][1])

    def test_functional(self):
        self.assertEqual([2, 3, 5], calc_nums(nums=[3, 4, 5]))


if __name__ == "__main__":
    main()
