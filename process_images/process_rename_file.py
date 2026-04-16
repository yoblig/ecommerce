import os
import pandas as pd
import re
import glob

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')


def normalize_filenames(folder):
    """Strip dashes, spaces, and underscores from image filenames to simplify matching.
    Returns a dict mapping normalized filename → original filename (before normalization)."""
    original_map = {}
    for file_name in os.listdir(folder):
        if not file_name.lower().endswith(IMAGE_EXTENSIONS):
            continue
        new_file_name = re.sub(r'[- _]', '', file_name)
        original_map[new_file_name] = file_name
        if new_file_name != file_name:
            os.rename(os.path.join(folder, file_name), os.path.join(folder, new_file_name))
    return original_map


def rename_images(folder_path, buyer_xlsx, assortment_csv, original_map):
    """Rename images using VENDOR_STYLE → ITEM_NAME → DATA_WEB_IMAGE_URL lookup."""
    # Load buyer XLSX: detect header row, then extract VENDOR STYLE # and description column
    df_raw = pd.read_excel(buyer_xlsx, header=None, engine='openpyxl')
    keywords = ['BOOKSTORE DESCRIPTION', 'NETSUITE DESCRIPTION', 'VENDOR STYLE #']
    header_row = next(
        (i for i, row in df_raw.iterrows() if any(k in str(cell) for cell in row for k in keywords)),
        None
    )
    if header_row is None:
        raise ValueError("Could not find header row in buyer XLSX.")

    buyer_df = pd.read_excel(buyer_xlsx, skiprows=header_row, engine='openpyxl')
    desc_col = next((c for c in buyer_df.columns if c in ['BOOKSTORE DESCRIPTION', 'NETSUITE DESCRIPTION', 'DESCRIPTION']), None)
    style_col = next((c for c in buyer_df.columns if 'VENDOR STYLE #' in str(c)), None)

    if not desc_col or not style_col:
        raise ValueError(f"Could not find required columns. Found: {buyer_df.columns.tolist()}")

    buyer_df = buyer_df[[desc_col, style_col]].dropna(how='all').dropna().copy()
    buyer_df.columns = ['ITEM_NAME', 'VENDOR_STYLE']
    buyer_df['VENDOR_STYLE'] = buyer_df['VENDOR_STYLE'].astype(str).str.strip()

    # Keep original vendor style (with dashes) for the log
    vendor_normalized_to_original = dict(zip(
        buyer_df['VENDOR_STYLE'].str.lower().str.replace(r'[- _]', '', regex=True),
        buyer_df['VENDOR_STYLE']
    ))
    vendor_to_item = dict(zip(
        buyer_df['VENDOR_STYLE'].str.lower().str.replace(r'[- _]', '', regex=True),
        buyer_df['ITEM_NAME'].astype(str).str.strip()
    ))

    # Load assortment CSV: ITEM_NAME + DATA_WEB_IMAGE_URL (other columns ignored)
    assortment_df = pd.read_csv(assortment_csv, usecols=['ITEM_NAME', 'DATA_WEB_IMAGE_URL'])
    item_to_url = dict(zip(
        assortment_df['ITEM_NAME'].astype(str).str.strip(),
        assortment_df['DATA_WEB_IMAGE_URL'].astype(str).str.strip()
    ))

    used_names = {}
    log = []

    for filename in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)
        if not os.path.isfile(file_path) or not filename.lower().endswith(IMAGE_EXTENSIONS):
            continue

        original_filename = original_map.get(filename, filename)

        # Match normalized filename against normalized VENDOR_STYLE
        matched_key = None
        for vendor_key in vendor_to_item:
            if vendor_key in filename.lower():
                matched_key = vendor_key
                break

        if not matched_key:
            print(f"⚠️  No vendor match: {filename}")
            log.append({
                'STATUS': 'No vendor match',
                'ITEM_NAME': '',
                'VENDOR_STYLE': '',
                'ORIGINAL_FILENAME': original_filename,
                'NEW_FILENAME': ''
            })
            continue

        item_name = vendor_to_item[matched_key]
        original_vendor_style = vendor_normalized_to_original[matched_key]

        # Look up DATA_WEB_IMAGE_URL using ITEM_NAME
        web_image_url = item_to_url.get(item_name)
        if not web_image_url:
            print(f"⚠️  No assortment match for ITEM_NAME '{item_name}': {filename}")
            log.append({
                'STATUS': 'No assortment match',
                'ITEM_NAME': item_name,
                'VENDOR_STYLE': original_vendor_style,
                'ORIGINAL_FILENAME': original_filename,
                'NEW_FILENAME': ''
            })
            continue

        # Handle incrementing if multiple images share the same base URL
        match = re.match(r"^(.*?)(\d+)$", web_image_url)
        if match:
            base_name = match.group(1)
            initial_number = int(match.group(2))
        else:
            base_name = web_image_url
            initial_number = 1

        if base_name in used_names:
            used_names[base_name] += 1
        else:
            used_names[base_name] = initial_number

        new_name = f"{base_name}{used_names[base_name]}{os.path.splitext(filename)[1]}"
        os.rename(file_path, os.path.join(folder_path, new_name))

        print(f"✅ {filename} → {new_name}")
        log.append({
            'STATUS': 'Renamed',
            'ITEM_NAME': item_name,
            'VENDOR_STYLE': original_vendor_style,
            'ORIGINAL_FILENAME': original_filename,
            'NEW_FILENAME': new_name
        })

    # Find assortment items with no image matched
    matched_items = {row['ITEM_NAME'] for row in log if row['STATUS'] == 'Renamed'}
    for item_name in sorted(item_to_url.keys()):
        if item_name not in matched_items:
            log.append({
                'STATUS': 'No image match',
                'ITEM_NAME': item_name,
                'VENDOR_STYLE': '',
                'ORIGINAL_FILENAME': '',
                'NEW_FILENAME': ''
            })

    # Save log CSV
    status_order = {'Renamed': 0, 'No image match': 1, 'No assortment match': 2, 'No vendor match': 3}
    log_df = pd.DataFrame(log, columns=['STATUS', 'ITEM_NAME', 'VENDOR_STYLE', 'ORIGINAL_FILENAME', 'NEW_FILENAME'])
    log_df = log_df.sort_values('STATUS', key=lambda s: s.map(status_order)).reset_index(drop=True)
    log_path = os.path.join(folder_path, 'rename_log.csv')
    log_df.to_csv(log_path, index=False)
    print(f"\n📋 Log saved to: {log_path}")


if __name__ == "__main__":
    folder_path = './process_images_input'

    # Auto-detect files inside the input folder
    buyer_files = [f for f in glob.glob(os.path.join(folder_path, "*.xlsx")) if 'buyer' in f.lower() and not os.path.basename(f).startswith("~$")]
    assortment_files = [f for f in glob.glob(os.path.join(folder_path, "*.csv")) if 'assortment' in f.lower()]

    if not buyer_files:
        raise FileNotFoundError("No buyer XLSX file found in process_images_input/.")
    if not assortment_files:
        raise FileNotFoundError("No assortment CSV file found in process_images_input/.")

    print(f"Buyer XLSX: {buyer_files[0]}")
    print(f"Assortment CSV: {assortment_files[0]}")

    original_map = normalize_filenames(folder_path)
    rename_images(folder_path, buyer_files[0], assortment_files[0], original_map)
