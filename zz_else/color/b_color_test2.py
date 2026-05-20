from utils import *

tests = [
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]

for vx, vy in tests:
    idx, name, color = vector_sector(vx, vy)
    print((vx, vy), idx, name, color)