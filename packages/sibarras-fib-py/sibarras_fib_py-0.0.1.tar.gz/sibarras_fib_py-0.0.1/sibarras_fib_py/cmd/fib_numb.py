import argparse

from sibarras_fib_py.fib_calcs.fib_number import recurring_fibonacci_number

def fib_numb() -> None:
    parser = argparse.ArgumentParser(
        description='Calculate Fibonacci Numbers')
    
    parser.add_argument(
        '--number',
        action='store',
        type=int,
        required=True,
        help="Fibonacci number to be calculated"
        )
    
    args = parser.parse_args()
    print("Your Fibonacci number is: "
        f"{recurring_fibonacci_number(number=args.number)}"
        )