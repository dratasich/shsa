#!/usr/bin/python3
"""
Profile.
"""

import argparse
import pstats


# parse args
desc = "Profile stats."
parser = argparse.ArgumentParser(description=desc)
parser.add_argument(dest='profile',
                    help="""Path to profile results.""")
args = parser.parse_args()

p = pstats.Stats(args.profile)
p.sort_stats('cumulative').print_stats()
