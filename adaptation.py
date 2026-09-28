def classify_depth(depth):
    if depth <= 30:
        return 1
    elif depth <= 70:
        return 2
    else:
        return 3


def classify_turbidity(turbidity):
    if turbidity <= 300:
        return 1
    elif turbidity <= 700:
        return 2
    else:
        return 3


def classify_battery(battery):
    if battery > 65:
        return "HIGH"
    elif battery >= 40:
        return "STANDARD"
    else:
        return "ECO"


def adaptation_algorithm(depth, turbidity, battery):

    depth_level = classify_depth(depth)
    turbidity_level = classify_turbidity(turbidity)

    environment_score = depth_level + turbidity_level

    if environment_score <= 3:
        environment = "EASY"
    elif environment_score == 4:
        environment = "MODERATE"
    else:
        environment = "DIFFICULT"

    battery_level = classify_battery(battery)

    conditions = {
        ("EASY", "HIGH"): "A1",
        ("EASY", "STANDARD"): "A2",
        ("EASY", "ECO"): "A3",

        ("MODERATE", "HIGH"): "A4",
        ("MODERATE", "STANDARD"): "A5",
        ("MODERATE", "ECO"): "A6",

        ("DIFFICULT", "HIGH"): "A7",
        ("DIFFICULT", "STANDARD"): "A8",
        ("DIFFICULT", "ECO"): "A9"
    }

    algorithm = conditions[(environment, battery_level)]

    profiles = {
        "A1": {
            "f0": 400000,
            "BW": 100000,
            "T": 0.002,
            "A": 0.90,
            "mode": "HIGH_PERFORMANCE"
        },

        "A2": {
            "f0": 300000,
            "BW": 80000,
            "T": 0.0015,
            "A": 0.70,
            "mode": "BALANCED"
        },

        "A3": {
            "f0": 200000,
            "BW": 50000,
            "T": 0.001,
            "A": 0.40,
            "mode": "ENERGY_SAVING"
        },

        "A4": {
            "f0": 350000,
            "BW": 90000,
            "T": 0.002,
            "A": 0.85,
            "mode": "PERFORMANCE_BIASED"
        },

        "A5": {
            "f0": 280000,
            "BW": 70000,
            "T": 0.0015,
            "A": 0.65,
            "mode": "BALANCED_ADAPTIVE"
        },

        "A6": {
            "f0": 180000,
            "BW": 40000,
            "T": 0.001,
            "A": 0.35,
            "mode": "CONSERVATIVE"
        },

        "A7": {
            "f0": 300000,
            "BW": 100000,
            "T": 0.002,
            "A": 1.00,
            "mode": "MAXIMUM_CAPABILITY"
        },

        "A8": {
            "f0": 250000,
            "BW": 80000,
            "T": 0.0015,
            "A": 0.75,
            "mode": "ROBUST_BALANCED"
        },

        "A9": {
            "f0": 150000,
            "BW": 40000,
            "T": 0.0008,
            "A": 0.30,
            "mode": "EMERGENCY_SAVING"
        }
    }

    result = profiles[algorithm]

    return {
        "environment_score": environment_score,
        "environment": environment,
        "battery": battery_level,
        "algorithm": algorithm,
        "f0": result["f0"],
        "BW": result["BW"],
        "T": result["T"],
        "A": result["A"],
        "mode": result["mode"]
    }


result = adaptation_algorithm(60, 800, 50)

print(result)