def recurring_fib_num(num: int) -> int:
    if num < 0:
        raise ValueError("Fibonacci has to be equal or above zero.")
    elif num <= 1:
        return num
    else:
        return recurring_fib_num(num - 1) + recurring_fib_num(num - 2)
