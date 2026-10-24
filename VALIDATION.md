# Validation record

Checked on 2026-10-02 in the delivery environment, using Python 3.14.2 with existing NumPy, Pillow, OpenCV and Plotly packages. Recommended end-user setup is Python 3.11/3.12 for native dependency compatibility.

## Executed

- Seven automated tests: center-of-mass weights and translation invariance; missing-pose and short-gap behavior; keyframe endpoints; all-missing data; complete PNG/JSON/CSV/AVI/ZIP export with video decoding and overwrite protection; visible/hidden overlay differences; real video decoding and sampling through a mocked pose detector.
- CLI synthetic demo: 71 output frames at 24 FPS, full PNG sequence, important frames, JSON/CSV, and MJPEG AVI.
- Inspected a rendered demo PNG visually.
- Compiled all Python source files for syntax checking.
- Constructed and serialized the interactive Plotly figure, and exercised JPEG export.

The demo is synthetic. A mocked detector verifies video plumbing and timestamp handling, not recognition quality.

## Not verified

- Windows launcher execution: `Setup-Windows.bat` and `Start-Windows.bat` were added and inspected, but this delivery environment is macOS. A Windows 10/11 smoke test is required before claiming Windows validation.
- Actual MediaPipe installation, model download, or real-video inference: MediaPipe is not installed in this environment.
- Streamlit UI runtime: Streamlit is not installed in this environment.
- Blender execution, generated GLB import or game-engine compatibility: Blender is not installed in this environment.
- Performance, memory use and recognition accuracy on an i5 7th-generation-class computer.
- A fully resolved dependency installation across Windows, macOS and Linux. Requirements specify version ranges, not a tested lockfile.

Before relying on the project, install the environment, process a short full-body human video, inspect inferred depth and gaps, then test the Blender command if GLB is needed. No scan-quality, biomechanical-accuracy, or real-time performance claim is made.
