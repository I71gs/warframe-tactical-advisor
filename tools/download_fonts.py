from __future__ import annotations
import urllib.request
from pathlib import Path

def download_fonts() -> None:
    root = Path(__file__).resolve().parents[1]
    fonts_dir = root / "src" / "resources" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    url = "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf"
    dest = fonts_dir / "Inter.ttf"
    
    print(f"Downloading Inter font to {fonts_dir}...")
    if not dest.exists():
        try:
            print("Fetching Inter.ttf...")
            urllib.request.urlretrieve(url, dest)
            print("Successfully downloaded Inter.ttf")
        except Exception as e:
            print(f"Failed to download Inter.ttf: {e}")
    else:
        print("Inter.ttf already exists.")

if __name__ == "__main__":
    download_fonts()
