import subprocess
from pathlib import Path

EXE_PATH = Path("/home/moritz/python_test/bbpPairings.exe")


def generate_dutch_pairings(input_file_path: Path, output_file_path: Path) -> None:
    cmd = [str(EXE_PATH), "--dutch", str(input_file_path), "-p", str(output_file_path)]
    subprocess.run(cmd, check=False)
