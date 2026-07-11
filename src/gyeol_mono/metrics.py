"""Cell and scale constraints for the duospace build."""

from dataclasses import dataclass

UNITS_PER_EM = 1_000
LATIN_ADVANCE = 600
CJK_ADVANCE = 1_200
CJK_GUARD = 12
CJK_SCALE_CANDIDATES = (1.00, 1.05, 1.10, 1.15)


@dataclass(frozen=True, slots=True)
class Cell:
    x_min: int
    x_max: int
    y_min: int
    y_max: int

    def __post_init__(self) -> None:
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            raise ValueError("cell bounds must have a positive width and height")

    @property
    def patcher_value(self) -> str:
        return f"{self.x_min}:{self.x_max}:{self.y_min}:{self.y_max}"


POWERLINE_CELL = Cell(x_min=0, x_max=600, y_min=-275, y_max=1_025)


def is_valid_advance(advance: int) -> bool:
    return advance in {LATIN_ADVANCE, CJK_ADVANCE}
