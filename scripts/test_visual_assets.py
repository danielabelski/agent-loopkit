from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

REQUIRED_ASSETS = {
    "logo.png": (1024, 1024),
    "logo-512.png": (512, 512),
    "icon.png": (256, 256),
    "icon-32.png": (32, 32),
    "banner.png": (1280, 640),
    "banner-compact.png": (1280, 320),
    "social-preview.png": (1280, 640),
}

SOURCE_ASSETS = [
    "source-logo-dark.jpg",
    "source-logo-light-checker.jpg",
    "source-banner.jpg",
    "source-social-preview.jpg",
]


def test_required_visual_assets_exist_and_have_expected_dimensions():
    for name, expected_size in REQUIRED_ASSETS.items():
        path = ASSETS / name
        assert path.exists(), f"missing {path}"
        assert path.stat().st_size > 1000, f"{path} looks empty or truncated"
        with Image.open(path) as image:
            assert image.size == expected_size
            assert image.mode in {"RGB", "RGBA"}


def test_source_assets_are_preserved_for_future_recrops():
    for name in SOURCE_ASSETS:
        path = ASSETS / name
        assert path.exists(), f"missing source asset {path}"
        assert path.stat().st_size > 10_000, f"{path} looks empty or truncated"


def test_brand_assets_do_not_contain_public_unsafe_strings():
    forbidden = ["+1 ", "wa.me", "tgohelpnow", "gmail.com", "sk-", "ghp_"]
    for path in list(ASSETS.glob("*.svg")) + list(ASSETS.glob("*.txt")):
        text = path.read_text(encoding="utf-8").lower()
        for needle in forbidden:
            assert needle.lower() not in text, f"{needle} leaked into {path}"
