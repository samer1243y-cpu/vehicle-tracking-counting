# Preparation changes — 2026-10-09

Recovered scripts used the signs of infinite lines, overlaid counting lines before inference, displayed a GUI unconditionally, and had scene-specific coordinates. The review copy adds a CLI, normalized configurable finite line segments, headless operation, video/CSV/JSON output, validation of FPS and arguments, and video-time speed estimation (opt-in only). A crossing is counted once per track and line, including a movement that touches the line before changing sides. Tests cover the finite-segment regression and duplicate counts.

These are portfolio-preparation changes, not features retroactively attributed to the original project. The checkpoint and local input video were used for validation only and are not distributed. No training or benchmark was conducted.
