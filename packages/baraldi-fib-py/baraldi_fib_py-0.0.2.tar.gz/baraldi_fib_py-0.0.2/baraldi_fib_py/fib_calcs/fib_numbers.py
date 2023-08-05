from typing import List

from .fib_number import recurring_fib_num


def calc_nums(nums: List[int]) -> List[int]:
    return [recurring_fib_num(num=i) for i in nums]
