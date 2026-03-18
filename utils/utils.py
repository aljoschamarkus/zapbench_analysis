from types import MappingProxyType

bounds = MappingProxyType(
    {
        "gain": [1, 648],
        'dots': [650, 2421],
        'flash': [2423, 3077],
        'taxis': [3079, 3734],
        'turning': [3736, 5046],
        'position': [5048, 5637],
        'open':  [5639, 6622],
        'rotation': [6624, 7278],
        'dark': [7280, 7878],
    }
)

# use as:
# bounds['turning'][0]

def display_bounds():
    for bound in bounds:
        print(f"{bound} has bounds: [{bounds[bound][0]}, {bounds[bound][1]}]")

def get_condition_bounds(condition):
    return bounds[condition][0], bounds[condition][1]