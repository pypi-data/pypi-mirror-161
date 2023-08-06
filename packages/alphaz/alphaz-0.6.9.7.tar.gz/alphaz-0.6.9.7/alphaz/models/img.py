
from .main import AlphaDataclass, dataclass

@dataclass
class AlphaImage(AlphaDataclass):
    uuid: str
    src: str
    alt: str
    source_url: str