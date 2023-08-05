import argparse

from baraldi_fib_py.fib_calcs.fib_number import recurring_fib_num


def fib_num() -> None:
    parser = argparse.ArgumentParser(description="Calculate Fibonacci numbers")
    parser.add_argument("--number", action="store",
                        type=int, required=True,
                        help="Fibonacci number to be calculated")
    args = parser.parse_args()
    print(f"Your Fibonacci number is: {recurring_fib_num(num=args.number)}")
