from unittest import main, TestCase

from baraldi_fib_py.fib_calcs.fib_number import recurring_fib_num


class RecurringFibNumberTest(TestCase):
    def test_zero(self):
        self.assertEqual(0, recurring_fib_num(num=0))

    def test_negative(self):
        with self.assertRaises(ValueError) as raised_error:
            recurring_fib_num(num=-1)
        self.assertEqual("Fibonacci has to be equal or above zero.", str(raised_error.exception))

    def test_one(self):
        self.assertEqual(1, recurring_fib_num(num=1))

    def test_two(self):
        self.assertEqual(1, recurring_fib_num(num=1))

    def test_twenty(self):
        self.assertEqual(6765, recurring_fib_num(num=20))


if __name__ == "__main__":
    main()
