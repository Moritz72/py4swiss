from py4swiss.engines.dutch.criteria.absolute import C1, C2, C3
from py4swiss.engines.dutch.criteria.color import E1, E2, E3, E4, E5
from py4swiss.engines.dutch.criteria.quality import (
    C5,
    C6,
    C7,
    C8,
    C9,
    C10,
    C11,
    C12,
    C13,
    C14,
    C15,
    C16,
    C17,
    C18,
    C19,
)

ABSOLUTE_CRITERIA = (C1, C2, C3)
COLOR_CRITERIA = (E1, E2, E3, E4, E5)
QUALITY_CRITERIA = (C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15, C16, C17, C18, C19)

__all__ = ["ABSOLUTE_CRITERIA", "COLOR_CRITERIA", "QUALITY_CRITERIA"]
