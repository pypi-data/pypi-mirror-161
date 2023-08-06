import random

import numpy.random


def seed_standard_library_and_numpy():
    random.seed(1)
    numpy.random.seed(1)
