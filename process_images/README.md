# Process Images

Crops whitespace, adds padding, and outputs standardized 1000×1000 JPGs.

## Setup

Create these two folders in this directory before running:

```
process_images_input/
process_images_output/
```

Place your images (PNG, JPG, JPEG, WEBP) in `process_images_input/` and the processed JPGs will be saved to `process_images_output/`.

## Usage

```
python process_images.py          # default padding (0.08)
python process_images.py 0.12     # more padding, useful for hats
```
