import argparse
import random
import sys

def concat(firstName, n):
    str = (firstName+' ')*n
    return str[:-1]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--firstName', type=str)
    parser.add_argument('--n', type=int)
    args = parser.parse_args()
    if random.random() < 0.2:
        print("Job failed.")
        sys.exit(1) 
    else:
        result = concat(args.firstName, args.n)
        print(result)