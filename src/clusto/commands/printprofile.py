import pstats
import sys

stats = pstats.Stats(sys.argv[1])
stats.sort_stats('calls')

stats.print_stats()
