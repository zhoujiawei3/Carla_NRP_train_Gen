#!/usr/bin/env bash
# Activate environment if needed (uncomment or replace for your shell)
# activate conda_carla

# Set vehicle blueprint here. Example: vehicle.tesla.model3 or vehicle.audi.etron
VEHICLE="vehicle.tesla.model3"
output_dir="C:/outputs/DTN/"

# Generate masks first (pass vehicle if needed)
python base_1world_DTN_9_mask.py --vehicle "$VEHICLE" --output_dir "$output_dir"

# Generate YOLO labels from masks (adjust paths as needed)
python get_label.py --input_dir "$output_dir/masks" --output_dir "$output_dir/train_label_new"

# Generate RGB datasets for a set of colors; each call passes the chosen vehicle blueprint
python base_1world_DTN_9.py --color=255,0,0 --vehicle "$VEHICLE" --output_dir "$output_dir"
python base_1world_DTN_9.py --color=0,255,0 --vehicle "$VEHICLE" --output_dir "$output_dir"
python base_1world_DTN_9.py --color=0,0,255 --vehicle "$VEHICLE" --output_dir "$output_dir"
python base_1world_DTN_9.py --color=255,255,0 --vehicle "$VEHICLE" --output_dir "$output_dir"
python base_1world_DTN_9.py --color=0,255,255 --vehicle "$VEHICLE" --output_dir "$output_dir"
python base_1world_DTN_9.py --color=255,0,255 --vehicle "$VEHICLE" --output_dir "$output_dir"
python base_1world_DTN_9.py --color=128,128,128 --vehicle "$VEHICLE"    --output_dir "$output_dir"
python base_1world_DTN_9.py --color=0,0,0 --vehicle "$VEHICLE" --output_dir "$output_dir"
python base_1world_DTN_9.py --color=255,255,255 --vehicle "$VEHICLE" --output_dir "$output_dir"




# python base_1world_DTN_64.py --color='0,0,0'
# python base_1world_DTN_64.py --color='0,0,85'
# python base_1world_DTN_64.py --color='0,0,170'
# python base_1world_DTN_64.py --color='0,0,255'
# python base_1world_DTN_64.py --color='0,85,0'
# python base_1world_DTN_64.py --color='0,85,85'
# python base_1world_DTN_64.py --color='0,85,170'
# python base_1world_DTN_64.py --color='0,85,255'
# python base_1world_DTN_64.py --color='0,170,0'
# python base_1world_DTN_64.py --color='0,170,85'
# python base_1world_DTN_64.py --color='0,170,170'
# python base_1world_DTN_64.py --color='0,170,255'
# python base_1world_DTN_64.py --color='0,255,0'
# python base_1world_DTN_64.py --color='0,255,85'
# python base_1world_DTN_64.py --color='0,255,170'
# python base_1world_DTN_64.py --color='0,255,255'
# python base_1world_DTN_64.py --color='85,0,0'
# python base_1world_DTN_64.py --color='85,0,85'
# python base_1world_DTN_64.py --color='85,0,170'
# python base_1world_DTN_64.py --color='85,0,255'
# python base_1world_DTN_64.py --color='85,85,0'
# python base_1world_DTN_64.py --color='85,85,85'
# python base_1world_DTN_64.py --color='85,85,170'
# python base_1world_DTN_64.py --color='85,85,255'
# python base_1world_DTN_64.py --color='85,170,0'
# python base_1world_DTN_64.py --color='85,170,85'
# python base_1world_DTN_64.py --color='85,170,170'
# python base_1world_DTN_64.py --color='85,170,255'
# python base_1world_DTN_64.py --color='85,255,0'
# python base_1world_DTN_64.py --color='85,255,85'
# python base_1world_DTN_64.py --color='85,255,170'
# python base_1world_DTN_64.py --color='85,255,255'
# python base_1world_DTN_64.py --color='170,0,0'
# python base_1world_DTN_64.py --color='170,0,85'
# python base_1world_DTN_64.py --color='170,0,170'
# python base_1world_DTN_64.py --color='170,0,255'
# python base_1world_DTN_64.py --color='170,85,0'
# python base_1world_DTN_64.py --color='170,85,85'
# python base_1world_DTN_64.py --color='170,85,170'
# python base_1world_DTN_64.py --color='170,85,255'
# python base_1world_DTN_64.py --color='170,170,0'
# python base_1world_DTN_64.py --color='170,170,85'
# python base_1world_DTN_64.py --color='170,170,170'
# python base_1world_DTN_64.py --color='170,170,255'
# python base_1world_DTN_64.py --color='170,255,0'
# python base_1world_DTN_64.py --color='170,255,85'
# python base_1world_DTN_64.py --color='170,255,170'
# python base_1world_DTN_64.py --color='170,255,255'
# python base_1world_DTN_64.py --color='255,0,0'
# python base_1world_DTN_64.py --color='255,0,85'
# python base_1world_DTN_64.py --color='255,0,170'
# python base_1world_DTN_64.py --color='255,0,255'
# python base_1world_DTN_64.py --color='255,85,0'
# python base_1world_DTN_64.py --color='255,85,85'
# python base_1world_DTN_64.py --color='255,85,170'
# python base_1world_DTN_64.py --color='255,85,255'
# python base_1world_DTN_64.py --color='255,170,0'
# python base_1world_DTN_64.py --color='255,170,85'
# python base_1world_DTN_64.py --color='255,170,170'
# python base_1world_DTN_64.py --color='255,170,255'
# python base_1world_DTN_64.py --color='255,255,0'
# python base_1world_DTN_64.py --color='255,255,85'
# python base_1world_DTN_64.py --color='255,255,170'
# python base_1world_DTN_64.py --color='255,255,255'
