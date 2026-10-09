# Vehicle Tracking and Line Counting

A local video-analysis prototype by **Samer Weryam**, an AI student at Taibah University. It detects vehicles with YOLOv8, maintains track IDs with ByteTrack, and counts crossings of configurable line segments.

## What works

- Vehicle classes: car, motorcycle, bus, and truck (COCO IDs 2, 3, 5, 7).
- Persistent tracking and one crossing per track ID per counting line.
- Headless processing, optional preview, and optional annotated video output.
- Crossing-event CSV and a JSON execution summary.
- Optional experimental speed from a user-provided constant pixel-to-meter scale and **video timestamps**. Camera calibration and perspective correction remain necessary.

This release adapts the recovered `Tracking&Crossing.py` and `Tracing&Crossing.py`. The original produced a text report; CSV export and a command-line interface were added during portfolio preparation. The recovered `Speed.py` used processing wall-clock time and a fixed scale; its outputs are not validated physical speeds.

## Install and run

Reviewed with Python 3.13, CPU PyTorch 2.10.0, Ultralytics 8.4.14, and OpenCV 4.13.0.

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python traffic.py --video path/to/authorized-video.mp4 --model yolov8n.pt --save-video
```

Ultralytics downloads the named model if it is not available locally. For an offline run, provide the path to an existing checkpoint. Model weights and video footage are excluded from this repository. Use footage that you are permitted to process and share.

Define lines with normalized coordinates (`x1,y1,x2,y2`, all in `[0,1]`):

```bash
python traffic.py --video input.mp4 --line A:0.1,0.5,0.9,0.5 --max-frames 240
python -m unittest discover -s tests -v
```

Default lines are inherited from the recovered highway scripts. Adjust them to your scene. Results appear in `runs/traffic/crossings.csv` and `runs/traffic/summary.json`; `--save-video` adds `annotated.mp4`. Use a different `--output` directory to preserve earlier runs.

## Evidence and limitations

See [validation](docs/VALIDATION.md) and [the actual execution summary](docs/smoke-summary.json). This is an execution check on local footage, not a ground-truth evaluation. No tracking accuracy, vehicle-count accuracy, or speed-accuracy score is claimed.

- Camera motion, occlusion, ID changes and ID reuse can affect counting.
- Memory tracks IDs for the entire video; very long streams require a lifecycle strategy.
- A vehicle moving between counting lines may contribute to both line totals. Their sum is crossing events, not unique vehicles.
- Counted segments are finite; crossings of their infinite extension are excluded.
- Constant-scale speed is uncalibrated and disabled by default. No perspective compensation is implemented.
- No drone flight control, illegal-parking detector, congestion classifier, or custom training is included.

## Attribution and release

Built on [Ultralytics](https://github.com/ultralytics/ultralytics), [OpenCV](https://opencv.org/), and [ByteTrack](https://github.com/ifzhang/ByteTrack). Review their upstream license terms before reuse or deployment. No project reuse license was selected during this portfolio review. This release does not grant rights to model weights or third-party footage.

Recovered-source hashes and preparation changes are recorded in `docs/`. The originals were preserved and no earlier completion date is claimed.
