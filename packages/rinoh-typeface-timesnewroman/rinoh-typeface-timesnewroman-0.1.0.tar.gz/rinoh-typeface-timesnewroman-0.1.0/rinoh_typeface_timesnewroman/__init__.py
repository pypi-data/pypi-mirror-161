
from pathlib import Path

from rinoh.font import Typeface
from rinoh.font.opentype import OpenTypeFont


__all__ = ['typeface']


DIR = Path(__file__).parent
FONTS = [OpenTypeFont(ttf) for ttf in [*DIR.glob('*.TTF'), *DIR.glob('*.ttf')]]

typeface = Typeface('Times New Roman', *FONTS)
