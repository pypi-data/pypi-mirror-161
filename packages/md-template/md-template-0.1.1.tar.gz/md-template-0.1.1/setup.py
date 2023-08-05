import json
import os

from setuptools import setup

NATSORT_REQUIRES = [
    "natsort>=8.1.0,<9",
]

EXTRAS_REQUIRES = {
    "natsort": NATSORT_REQUIRES,
    "full": [
        *NATSORT_REQUIRES,
        "PyYAML>=6.0,<7.0",
    ],
}

if os.path.exists("package-data.json"):
    with open("package-data.json") as file:
        data = json.loads(file.read())
else:
    data = {}

if __name__ == "__main__":
    setup(extras_require=EXTRAS_REQUIRES, **data)
