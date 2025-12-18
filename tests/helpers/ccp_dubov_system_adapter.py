from pathlib import Path

from py4swiss.trf.codes import XCode


class CppDubovSystemAdapter:
    """A helper class to transform data for CPPDubovSystem."""

    SUFFIX: str = "_dubov"

    @staticmethod
    def _is_supported_code(line: str) -> bool:
        """Check whether the given line is supported (does not start with either of XXC or XXS)."""
        return not line.startswith(XCode.CONFIGURATIONS) and not line.startswith(XCode.POINT_SYSTEM)

    @classmethod
    def get_suffixed_path(cls, path: Path) -> Path:
        """Return the suffixed path to the given poth."""
        return path.with_stem(path.stem + cls.SUFFIX)

    @classmethod
    def transform_trf(cls, input_path: Path, output_path: Path | None = None) -> None:
        """Remove the codes XXC and XXS from the given TRF."""
        lines = input_path.read_text(encoding="utf-8").splitlines(keepends=True)
        lines = [line for line in lines if cls._is_supported_code(line)]

        output_path = output_path or cls.get_suffixed_path(input_path)
        output_path.write_text("".join(lines), encoding="utf-8")

    @classmethod
    def transform_pairings(cls, input_path: Path, output_path: Path | None = None) -> None:
        """Convert the pairings csv file to a simple txt file."""
        text = input_path.read_text(encoding="utf-8")

        text = text.replace(",-1", ",0")
        text = text.replace(",", " ")

        output_path = output_path or cls.get_suffixed_path(input_path)
        output_path.write_text(text, encoding="utf-8")
