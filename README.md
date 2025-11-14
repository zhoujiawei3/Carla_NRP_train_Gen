DTN_train_generate
===================

Purpose
-------
This small toolset generates RGB images and semantic masks from CARLA for DTN training.

Files
-----
- `base_1world_DTN_9.py` — RGB image generator. Now accepts: `--color`, `--output_dir`, and `--vehicle`.
- `base_1world_DTN_9_mask.py` — Semantic segmentation mask generator. Now accepts: `--color`, `--output_dir`, and `--vehicle`.
- `script.sh` — Example batch script that runs mask generation and multiple color variants. It defines a `VEHICLE` variable which is passed to the Python scripts.
- `script.sh` — Example batch script that runs mask generation and multiple color variants. It defines a `VEHICLE` variable which is passed to the Python scripts.
- `get_label.py` — Convert mask images into YOLO-format label `.txt` files. Accepts `--input_dir` and `--output_dir`.

Usage
-----
Run the scripts from the `DTN_train_generate` directory. Examples below assume a bash-like shell.

Generate masks only (using default vehicle):

```bash
python base_1world_DTN_9_mask.py --output_dir "C:/outputs/DTN/" --vehicle "vehicle.audi.etron"
```

Generate RGB images for one color and vehicle:

```bash
python base_1world_DTN_9.py --color 255,255,255 --output_dir "C:/outputs/DTN/" --vehicle "vehicle.tesla.model3"
```

Use the provided `script.sh` to run a batch for multiple colors. Edit the `VEHICLE` variable at the top of `script.sh` to change the vehicle model used for all runs.

Generate YOLO labels from masks (after running the mask script):

```bash
python get_label.py --input_dir "C:/outputs/DTN/masks" --output_dir "C:/outputs/DTN/train_label_new"
```

Notes & tips
-----------
- `--vehicle` expects a CARLA blueprint id (e.g. `vehicle.tesla.model3`, `vehicle.audi.etron`). If the blueprint id is not found the script prints a short sample of available vehicle ids and exits.
- `--output_dir` is the base directory used by both scripts; the mask script will use a `masks` subfolder by default.
- The scripts attempt to be robust to brief disk-write latency when saving images, but if you run them on a slow or network-mounted drive you may need to increase retry timings in the code.
- On Windows you can run `script.sh` with Git Bash or adapt it to PowerShell. For PowerShell replace the `VEHICLE` variable usage with PowerShell variable syntax.

If you want I can:
- Change hardcoded default output paths to always be under `--output_dir` (more consistent).
- Convert `script.sh` into a PowerShell `.ps1` wrapper.
- Add a small example that validates generated `.npz` files.
