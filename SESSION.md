# Session — 2026-04-16

## Goals
- [x] Add process_buyer_assortment tool
- [x] Add process_rename_file tool
- [x] Update process_images to only process renamed files and clean up input folder

## Tools / Scripts
| Tool | Status | Notes |
|------|--------|-------|
| process_images | Updated | Only processes `_media` files; clears input, copies log to output |
| process_rename_file | Done | Renames images via buyer XLSX + assortment CSV lookup; outputs rename_log.csv |
| process_buyer_assortment | Done | Extracts ITEM_NAME + VENDOR_STYLE from buyer xlsx to CSV |

## Workflow
1. Run `process_buyer_assortment.py` → outputs buyer CSV with ITEM_NAME + VENDOR_STYLE
2. Drop buyer XLSX, assortment CSV, and images into `process_images_input/`
3. Run `process_rename_file.py` → renames images, saves rename_log.csv
4. Run `process_images.py` → frames renamed images, clears input, copies log to output

## Notes
- Buyer file detected by `buyer` in filename (xlsx)
- Assortment file detected by `assortment` in filename (csv)
- Only images with `_media` in the filename are processed by process_images.py
