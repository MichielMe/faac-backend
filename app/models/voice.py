from enum import Enum
from typing import Dict


class Voice(str, Enum):
    MAN = "man"
    WOMAN = "woman"
    MAN_FLEMISH = "man_vl"
    WOMAN_FLEMISH = "woman_vl"


# Map each voice option to its Eleven Labs voice ID
VOICE_ID_MAPPING: Dict[Voice, str] = {
    Voice.MAN: "zwqMXWHsKBMIb9RPiWI0",
    Voice.WOMAN: "8z5UhJ1uv7X8TN5yg8oI",
    Voice.MAN_FLEMISH: "tRyB8BgRzpNUv3o2XWD4",
    Voice.WOMAN_FLEMISH: "ANHrhmaFeVN0QJaa0PhL",
}
