import argparse
from pathlib import Path

from py4swiss.engines import DutchEngine
from py4swiss.trf import TrfParser


def parse_args() -> argparse.Namespace:
    """Parse the provided arguments."""

    parser = argparse.ArgumentParser(
        prog="py4swiss",
        description="Produce a round pairing for the specified Swiss tournament TRF.",
    )

    parser.add_argument(
        "-t",
        "--trf",
        type=Path,
        required=True,
        help="path to the Swiss tournament TRF file containing the tournament standings",
    )

    parser.add_argument(
        "-e",
        "--engine",
        type=str,
        default="dutch",
        help="pairing engine used to generate the pairings (default: dutch)",
    )

    parser.add_argument(
        "-p",
        "--pairings",
        type=Path,
        default="pairings.txt",
        help="path to the output file containing the round pairing (default: pairings.txt)",
    )

    return parser.parse_args()


def main() -> None:
    """Generate pairings according to the provided specifications."""
    args = parse_args()

    match args.engine:
        case "dutch":
            engine = DutchEngine
        case _:
            raise ValueError(f"Invalid pairing engine '{args.engine}'")

    trf = TrfParser.parse(args.trf)
    pairings = engine.generate_pairings(trf)
    engine.write_pairings_to_file(pairings, args.pairings)
