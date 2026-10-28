import argparse
from pathlib import Path

import shutil

from package_common import REQUIRED_OCR_FILES, require_file


ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"


def configure_ocr_model(
    assets_dir: Path = ASSETS_DIR, ocr_dir: Path | None = None
) -> None:
    """保留完整的既有模型，或向指定目录导入默认 OCR 模型。"""
    ocr_dir = ocr_dir or assets_dir / "resource" / "base" / "model" / "ocr"
    if ocr_dir.exists():
        for name in REQUIRED_OCR_FILES:
            require_file(ocr_dir / name)
        print("Found existing OCR directory, skipping default OCR model import.")
        return

    source = assets_dir / "MaaCommonAssets" / "OCR" / "ppocr_v6" / "small"
    for name in REQUIRED_OCR_FILES:
        require_file(source / name)
    shutil.copytree(source, ocr_dir)


KR_OCR_SOURCES = {
    "det.onnx": ("MaaCommonAssets", "OCR", "ppocr_v6", "small"),
    "rec.onnx": ("models", "korean_PP-OCRv5_mobile_rec"),
    "keys.txt": ("models", "korean_PP-OCRv5_mobile_rec"),
    # 识别模型为 Apache-2.0，再分发时需附带许可证。
    "LICENSE": ("models", "korean_PP-OCRv5_mobile_rec"),
}


def configure_kr_ocr_model(
    assets_dir: Path = ASSETS_DIR, ocr_dir: Path | None = None
) -> None:
    """韩服 OCR：沿用通用 v6 检测模型，识别模型与字典使用韩文 PP-OCRv5（v6 不支持韩文）。"""
    ocr_dir = ocr_dir or assets_dir / "resource" / "kr" / "model" / "ocr"
    if ocr_dir.exists():
        for name in KR_OCR_SOURCES:
            require_file(ocr_dir / name)
        print("Found existing KR OCR directory, skipping KR OCR model import.")
        return

    sources = {
        name: assets_dir.joinpath(*parts, name)
        for name, parts in KR_OCR_SOURCES.items()
    }
    for source in sources.values():
        require_file(source)
    ocr_dir.mkdir(parents=True)
    for name, source in sources.items():
        shutil.copy2(source, ocr_dir / name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare the project OCR model.")
    parser.add_argument("--assets-dir", type=Path, default=ASSETS_DIR)
    parser.add_argument("--ocr-dir", type=Path)
    parser.add_argument("--kr-ocr-dir", type=Path)
    args = parser.parse_args()
    configure_ocr_model(args.assets_dir, args.ocr_dir)
    # 仅指定 --ocr-dir 的打包调用不应把韩服模型写进源码目录。
    if args.kr_ocr_dir or not args.ocr_dir:
        configure_kr_ocr_model(args.assets_dir, args.kr_ocr_dir)

    print("OCR model configured.")
