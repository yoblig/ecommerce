import os
import sys
import shutil
from PIL import Image
import numpy as np

def crop_and_frame(image, tolerance=245, frame_ratio=0.08):
    """
    Crops whitespace and adds balanced framing around the subject.
    - tolerance: how bright a pixel must be to count as "white" (240–250 typical)
    - frame_ratio: how much whitespace to preserve around the cropped object (0.1 = 10%)
    """
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        img = background
    else:
        img = image.convert("RGB")
    img_array = np.asarray(img)
    
    # Identify non-white area
    mask = (img_array < tolerance).any(axis=2)
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img  # no subject found
    
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    cropped = img.crop((x0, y0, x1, y1))
    
    # Add framing (balanced whitespace)
    width, height = cropped.size
    pad_x = int(width * frame_ratio)
    pad_y = int(height * frame_ratio)
    
    new_w = width + 2 * pad_x
    new_h = height + 2 * pad_y
    framed = Image.new("RGB", (new_w, new_h), (255, 255, 255))
    framed.paste(cropped, (pad_x, pad_y))
    
    return framed

def resize_and_center(image, target_size=(1000, 1000)):
    """
    Resizes proportionally (scales up or down) and centers image on a white 1000×1000 canvas.
    """
    if image.mode == 'RGBA':
        bg = Image.new('RGB', image.size, (255, 255, 255))
        bg.paste(image, mask=image.split()[3])
        image = bg

    # Calculate scaling factor to fit image within target size while maintaining aspect ratio
    width_ratio = target_size[0] / image.width
    height_ratio = target_size[1] / image.height
    scale_factor = min(width_ratio, height_ratio)

    # Resize image (scales up or down as needed)
    new_width = int(image.width * scale_factor)
    new_height = int(image.height * scale_factor)
    image = image.resize((new_width, new_height), Image.LANCZOS)

    # Center on white canvas
    background = Image.new("RGB", target_size, (255, 255, 255))
    offset_x = (target_size[0] - image.width) // 2
    offset_y = (target_size[1] - image.height) // 2
    background.paste(image, (offset_x, offset_y))
    return background

def process_images(input_folder, output_folder="process_images_output", tolerance=245, frame_ratio=0.08):
    """
    Processes all images in a folder:
    - Crops whitespace
    - Adds balanced frame
    - Resizes to 1000×1000
    - Saves as .JPG
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            continue
        if '_media' not in filename.lower():
            continue

        input_path = os.path.join(input_folder, filename)
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_folder, f"{base_name}.jpg")

        img = Image.open(input_path)
        framed = crop_and_frame(img, tolerance=tolerance, frame_ratio=frame_ratio)
        final = resize_and_center(framed)
        final.save(output_path, "JPEG", quality=80, optimize=True)
        print(f"✅ Saved: {output_path}")

    print("🎉 All images cropped, framed, resized, and exported as JPGs!")

    # Copy log to output folder, then remove all images from input folder
    log_path = os.path.join(input_folder, 'rename_log.csv')
    if os.path.exists(log_path):
        shutil.copy(log_path, os.path.join(output_folder, 'rename_log.csv'))

    for filename in os.listdir(input_folder):
        os.remove(os.path.join(input_folder, filename))

    print("🗑️  Input images removed. Log copied to output folder.")

frame_ratio = float(sys.argv[1]) if len(sys.argv) > 1 else 0.08
process_images("./process_images_input", frame_ratio=frame_ratio)