from typing import Optional


def recurring_fib_num(num: int) -> Optional[int]:
    if num < 0:
        return None
    elif num <= 1:
        return num
    else:
        return recurring_fib_num(num - 1) + recurring_fib_num(num - 2)
