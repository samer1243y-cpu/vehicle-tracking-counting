# Validation — 2026-10-09

Four counting unit tests passed: finite-segment crossing, exclusion of the line extension, touching then crossing with independent track IDs, and rejection of zero-length lines.

A headless CPU run processed the first 240 frames of a recovered local traffic video using the existing `yolov8n.pt` checkpoint. It wrote a decodable annotated MP4, a crossing CSV, and a JSON summary. It reported 1,670 tracked-box observations, 59 distinct track IDs, and three line-A crossing events (zero on line B). These are program outputs, not verified true counts. Speed was disabled. No benchmark labels or calibration were available.

The source video and annotated footage are retained locally for review and excluded from public release because their redistribution permissions were not established. No successful-image illustration or synthetic result was substituted for real evidence.

The validation environment was a new virtual environment with access to existing installed packages (`--system-site-packages`); no original project environment was modified. Dependencies were available locally. A completely fresh dependency installation has not been tested.
