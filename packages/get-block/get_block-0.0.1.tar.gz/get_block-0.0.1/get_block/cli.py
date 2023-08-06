
"""
The command-line interface for getBlock
"""
import argparse
import os

from .getBlock import getBlockTimestamp


def main():
    parser = argparse.ArgumentParser(
        description="From a block id get it's timestamp."
    )
    parser.add_argument( "-b",
        "--blockId", type=str,
        help="The hexadecimal id of the block."
    )
    parser.add_argument('--apiKey', default=os.environ.get('ETHERSCAN_API_KEY'))

    args = parser.parse_args()
    try:
        blockTimestamp = getBlockTimestamp(args.apiKey, args.blockId)
        print(f"Block created: {blockTimestamp}")
    except Exception:
        print("Error: Invalid block id. \n")
        parser.print_help()

if __name__ == "__main__":
    main()
