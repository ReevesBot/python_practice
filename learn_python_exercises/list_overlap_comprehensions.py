#!/usr/bin/python3

import random

print(set(random.sample(range(100), 12)).intersection(set(random.sample(range(100), 12))))
