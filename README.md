# MotionSketch

A small local Python project that turns a short, single-person video into an **approximate, hip-relative 3D mannequin animation**. It includes a browser interface, command-line interface, CPU pose estimation, center-of-mass overlay, important-frame selection, image/video exports, and an optional Blender converter.

This is an MVP, not a movie-to-3D scanning system. Source images cannot reveal hidden surfaces or uniquely determine depth. The output does not reproduce the actor's appearance, clothing, global travel, or environment.

## Start

**Windows is the primary delivery target.** Extract the ZIP, install 64-bit Python 3.11 or 3.12 with the Python launcher, then double-click **Setup-Windows.bat** once. After setup, double-click **Start-Windows.bat** whenever you want to use the app. See `WINDOWS-START-HERE.txt` for the full Windows walkthrough. These scripts do not require PowerShell activation or an execution-policy change. This is a source project with launch scripts, not a standalone EXE. Windows runtime testing is still pending.

Use **64-bit Python 3.11 or 3.12**. These are conservative targets for native MediaPipe wheels. Python 3.14 is not the recommended setup. Run commands from this folder.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m motionsketch.cli download-model
.venv\Scripts\python -m streamlit run app.py
```

macOS / Linux:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m motionsketch.cli download-model
.venv/bin/python -m streamlit run app.py
```

Open the local URL shown by Streamlit, usually `http://localhost:8501`. Keep the terminal open. Installation and downloading Google's Lite pose model require internet. Video inference and export then run locally. No cloud API key is required. To try the UI without inference, click **Try synthetic demo**; the pose model is unnecessary for that route.

If installing MediaPipe fails, verify that the selected interpreter is Python 3.11/3.12 and that a wheel is available for your OS/CPU. Some Linux installations need the OS `libGL` runtime for OpenCV. This project does not bundle Python, native dependencies, model weights, or Blender.

## Workflow

1. Download the pose model using the command or sidebar button.
2. Load a clip containing one fully visible human, preferably without camera movement or scene cuts.
3. Click **Analyze video**. The default processes at most the first 30 seconds, sampled at 12 FPS with a maximum image width of 640 pixels.
4. Scrub the frame slider and drag the 3D view to rotate. Toggle joints and estimated center of mass independently.
5. Choose PNG or JPEG, camera angle, important-frame count, and optionally every frame.
6. Click **Build animation and frame export**, then download the ZIP. Rebuild after changing settings.

The UI provides frame scrubbing. Continuous rendered playback is in the exported AVI; it has no audio. The interactive camera is separate from the export camera-angle control.

## Included features and limits

| Requirement | Implementation |
|---|---|
| Recognize a person | MediaPipe Pose Landmarker Lite, one human |
| Divide body into parts | 18 labeled anatomical/virtual joints with connected segments; not pixel-level body segmentation |
| Extract movement | 3D estimated positions, timestamps and confidence; head position and an approximate neck point, not full head/neck orientation |
| Center of gravity | Simplified segment-weighted center of mass; equivalent under uniform gravity |
| Show/hide joints and CoM | Interactive preview, rendered frames/video, and Blender export |
| Important frames | Pose-diversity sampling plus first/last usable frames |
| Insert frames | Linear interpolation across gaps of at most 0.20 seconds, followed by optional smoothing |
| 3D animation | JSON/CSV position sequence; optional animated rigid-part GLB and Blender scene |
| PNG/JPEG and video | Keyframes, optional full frame sequence, 960×720 MJPEG AVI |
| Animals, scanned meshes, furniture and terrain | Not included; each requires a separate reconstruction/tracking pipeline |
| Generative in-between images | Not included; interpolation is explicitly labeled |

Use short, constant-frame-rate clips. Timestamps are derived from frame index and nominal FPS; convert variable-frame-rate footage first if timing matters. One detected person does not provide persistent identity tracking. Multiple people and cuts can switch the tracked subject. Cartoon/nonhuman characters may fail even if vaguely humanoid.

Coordinates have x right, y up, z toward the viewer; units are the model's estimated meters. Each pose is centered at its pelvis. Camera movement, root travel and global scale are not recovered. The displayed grid is illustrative, not detected ground. The pose is not a calibrated 3D scan.

## Center of mass

`motionsketch/core.py` contains the complete segment table and calculation:

`whole_body_center = sum(segment_mass_fraction * segment_center)`

The head/neck weight is 0.081; trunk 0.497; each upper arm 0.028; forearm 0.016; hand 0.006; thigh 0.100; shank 0.0465; foot 0.0145. These deliberately simplified fixed fractions sum to one. Segment centers are approximated along landmark segments; virtual neck/head points do not reproduce full anatomy. These are generic modeling assumptions, not subject-specific measurements. Body shape, clothing, carried objects and nonstandard anatomy are not modeled. Do not interpret the marker as a biomechanically validated measurement.

Frames are accepted only when all derived joint confidences meet the threshold. This conservatively avoids estimating whole-body CoM from a partial body. Long gaps stay missing and render blank. JSON uses `null` for missing positions; CSV uses empty position cells. Interpolation and smoothing can change bone lengths and introduce lag; this MVP has no contact constraints or inverse kinematics.

## Command line

With the environment active:

```sh
python -m motionsketch.cli demo --out result-demo
python -m motionsketch.cli analyze your-video.mp4 --out result-video --seconds 30 --sample-fps 12 --fps 24
python -m motionsketch.cli analyze your-video.mp4 --out result-frames --format jpeg --all-frames --hide-com
python -m unittest discover -s tests -v
```

Each export needs an empty destination directory. Output includes `motion.json`, `motion.csv`, `keyframes/`, optional `frames/`, `preview.avi`, `blender_export.py`, and `EXPORT_NOTES.txt`, plus an adjacent ZIP. Codec failure is reported; other exports still work. Keyframes are **renders of the estimated pose**, not original movie screenshots. A requested maximum count may yield fewer frames for very short clips.

## Blender / game-engine path

Install Blender separately if you want GLB. From an extracted result directory, using Blender 4.2 or newer:

```sh
blender --background --python blender_export.py -- motion.json character.glb
```

This also saves `character.blend`. The converter creates animated rigid cylinders and spheres, combining object motion into a scene animation. It does **not** create a skinned humanoid armature or perform retargeting. Import the GLB as a motion-reference mannequin in an engine that supports glTF object animation. To drive an existing game character, add a retargeting/IK stage matching its skeleton. The script resets the current Blender scene, so use the background command above rather than an unsaved interactive scene.

## Modest-computer settings

The target is an i5 7th-generation-class or newer CPU, a 64-bit OS, and approximately 8 GB RAM. This is a design target, **not a measured minimum or real-time guarantee**. CPU generation alone cannot determine performance. No discrete GPU is required by this implementation.

Start at 480–640 px, 6–12 analyzed FPS, 15–30 second clips, and 12–24 output FPS. Video is decoded sequentially; sampled images are not retained. Pose arrays are small; output images, video encoding and the in-memory ZIP can consume more space. Large uploads are limited by Streamlit's default upload cap. Work in short clips before raising limits. The UI deliberately caps each analysis at 120 seconds.

## Layout

```text
app.py                 Local Streamlit interface
blender_export.py      Optional animated GLB/BLEND exporter
motionsketch/core.py    Joint mapping, CoM, interpolation, smoothing, keyframes
motionsketch/tracking.py Video decoding and CPU pose inference
motionsketch/render.py  Interactive 3D plot and image renderer
motionsketch/export.py  JSON, CSV, images, AVI and ZIP
motionsketch/cli.py     Command-line entry point
tests/test_motion.py   Numerical and export checks
```

## Next projects after this MVP

1. **Game-character retargeter:** fit constant bone lengths, estimate joint rotations, add foot contact/IK, export a standard armature.
2. **Animal motion:** choose one species, a compatible pose model, and species-specific skeleton/mass assumptions; do not apply the human model.
3. **Environment reconstruction:** separate camera tracking, depth and multi-view scene reconstruction; moving actors and shot cuts require additional handling.

Keep these separate until each can be validated. Full textured movie reconstruction and generative video would substantially increase compute requirements.

## References

- [MediaPipe Pose Landmarker Python guide](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python)
- [MediaPipe models and capabilities](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker)
- [OpenCV video reading and writing](https://opencv.org/reading-and-writing-videos-using-opencv/)
- [Blender glTF export API](https://docs.blender.org/api/current/bpy.ops.export_scene.html)
- [Blender glTF import API](https://docs.blender.org/api/current/bpy.ops.import_scene.html)

Third-party software and downloaded weights remain subject to their own licenses. See `VALIDATION.md` for what was actually checked in the delivery environment.
