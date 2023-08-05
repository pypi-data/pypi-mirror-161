import numpy as np
import math

def get_mutual_rank(rankA2B, rankB2A):
    return math.sqrt(rankA2B*rankB2A)

