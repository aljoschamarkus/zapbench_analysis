from pathlib import Path
from PIL import Image


def pngs_to_webp(
    input_dir,
    output_webp,
    fps=10,
    crop_left=0,
    crop_top=0,
    crop_right=0,
    crop_bottom=0,
):
    input_path = Path(input_dir)
    png_files = sorted(input_path.glob("*.png"))

    if not png_files:
        raise ValueError("No PNG files found.")

    frames = []

    for file in png_files:
        img = Image.open(file).convert("RGBA")
        w, h = img.size
        img = img.crop((crop_left, crop_top, w - crop_right, h - crop_bottom))
        frames.append(img)

    size = frames[0].size
    for frame in frames:
        if frame.size != size:
            raise ValueError("All cropped frames must have the same size.")

    duration_ms = int(1000 / fps)

    frames[0].save(
        output_webp,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        lossless=True,
    )

    print(f"Saved WebP: {output_webp}")

pngs_to_webp(
    input_dir="/Users/aljoscha/Desktop/zap_no_segs",
    output_webp="/Users/aljoscha/Desktop/output2.webp",
    fps=1,
    crop_left=0,
    crop_top=250,
    crop_right=1000,
    crop_bottom=100,)