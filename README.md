# Macro Generator

A simple GUI tool for generating grazing SPEC macro files at BL1-5. Instead of writing macros by hand, you fill out a form and it spits out a ready-to-run macro file.

## What it does

- Generates grazing experiment macros for SAXS, WAXS, or both

## Requirements

- Python 3.x
- tkinter (usually comes with Python)

## How to run

## Quick start

1. **Pick a save location** - Click "Select Home Directory" and choose where you want the macro saved
2. **Name your macro** - No spaces allowed, use underscores (e.g., `my_experiment_001`)
3. **Set your scan parameters** - Exposure time, number of images, loops, etc.
4. **Add sample info** - Type in the location in gx, gy and the theta angle
5. **Hit "Save Macro File"** - You'll get a command to copy into SPEC


## Tips

- The "Same as macro" button copies your macro name to the data folder field
- Dark collection is optional 

## Troubleshooting


**Macro won't run in SPEC** - Make sure there are no spaces in your macro name.

---

*Katerina Reynolds, 2025*