from __future__ import annotations

import argparse
from pathlib import Path

from simulation.model import FreightSimulationModel


def main():
    start_model = FreightSimulationModel(num_trucks=5)
    start_model.step()

if __name__ == "__main__":
    main()
