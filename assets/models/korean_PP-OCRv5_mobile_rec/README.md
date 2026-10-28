# Korean PP-OCRv5 mobile recognition model

This directory contains the ONNX conversion of PaddlePaddle's
`korean_PP-OCRv5_mobile_rec` and its matching CTC character dictionary.
It replaces only the Korean recognition model and dictionary. Detection remains
the existing PP-OCRv6 small model; the separate `numeric` model is unchanged.

## Source and license

- Original model: [PaddlePaddle/korean_PP-OCRv5_mobile_rec](https://huggingface.co/PaddlePaddle/korean_PP-OCRv5_mobile_rec/tree/c02ecaf1f22bfd1c618cce154fd19185b47e663a)
- Pinned revision: `c02ecaf1f22bfd1c618cce154fd19185b47e663a`
- Original authors: PaddlePaddle / PaddleOCR contributors.
- License: Apache-2.0; see the accompanying `LICENSE` file.
- Changes: converted the original Paddle inference model to ONNX and exported
  `PostProcess.character_dict` from the original `inference.yml` to UTF-8 `keys.txt`.
  Model weights were not retrained. Conversion date: 2026-10-13 (KST).

## Conversion

Windows conversion environment: PaddlePaddle 3.1.1, Paddle2ONNX 2.1.0,
ONNX 1.17.0. Download `inference.json`, `inference.pdiparams` and `inference.yml`
from the pinned source above, then run:

```text
paddle2onnx --model_dir official_v5 --model_filename inference.json --params_filename inference.pdiparams --save_file rec.onnx --opset_version 11 --enable_onnx_checker True --optimize_tool None
```

Dictionary export uses the original order without filtering or sorting:

```python
from pathlib import Path
import yaml

config = yaml.safe_load(Path("official_v5/inference.yml").read_text(encoding="utf-8"))
characters = config["PostProcess"]["character_dict"]
Path("keys.txt").write_bytes(("\r\n".join(characters) + "\r\n").encode("utf-8"))
```

The ONNX graph uses opset 11 / IR 6, BGR input `[N, 3, 48, W]` and CTC output
`[N, T, 11947]`: 11,945 dictionary entries plus blank and space.
The validated dictionary uses CRLF line endings; Git preserves its bytes.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `rec.onnx` | 13,421,725 | `4bd4bd7079acff5252839d4a69faa4af6b7d863e941c8e401896068954bf3a45` |
| `keys.txt` | 59,396 | `2193f5dd0c62a4f268902b5d96dadfec3908d299afa9a6e5cad2c6a96c772828` |

## Validation and packaging scope

The converted model ran with the MaaFramework 5.14.3 native runtime on Windows
using CPU and DirectML. Paddle, ONNX and MaaFramework recognized the same
strings on 12 conversion parity samples; maximum absolute tensor error was
`3.9935112e-6`.

On 202 manually transcribed regions from 16 saved Korean server screenshots,
ignoring whitespace, exact matches increased from 140/202 (`ppocr_v3/ko_kr`)
to 186/202 (v5).

`tools/ci/configure.py` copies `rec.onnx`, `keys.txt` and this `LICENSE`,
together with the PP-OCRv6 small `det.onnx`, into new Korean OCR directories
(`resource/kr/model/ocr`). Existing complete OCR directories are preserved, as
with the default OCR model. `rec.onnx` and `keys.txt` must always be replaced
together.
