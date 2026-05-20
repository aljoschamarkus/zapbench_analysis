from pathlib import Path
from PIL import Image


def pngs_side_by_side_to_webp(
    left_dir,
    right_dir,
    output_webp,
    fps=10,
    crop_left=0,
    crop_top=0,
    crop_right=0,
    crop_bottom=0,
):
    left_path = Path(left_dir)
    right_path = Path(right_dir)

    left_files = sorted(left_path.glob("*.png"))
    right_files = sorted(right_path.glob("*.png"))

    if not left_files:
        raise ValueError(f"No PNG files found in left folder: {left_dir}")
    if not right_files:
        raise ValueError(f"No PNG files found in right folder: {right_dir}")

    if len(left_files) != len(right_files):
        raise ValueError(
            f"Folder mismatch: left has {len(left_files)} PNGs, right has {len(right_files)} PNGs"
        )

    frames = []

    for left_file, right_file in zip(left_files, right_files):
        left_img = Image.open(left_file).convert("RGBA")
        right_img = Image.open(right_file).convert("RGBA")

        lw, lh = left_img.size
        rw, rh = right_img.size

        # Apply same crop to both
        left_img = left_img.crop((crop_left, crop_top, lw - crop_right, lh - crop_bottom))
        right_img = right_img.crop((crop_left, crop_top, rw - crop_right, rh - crop_bottom))

        if left_img.size != right_img.size:
            raise ValueError(
                f"Cropped sizes do not match:\n"
                f"{left_file.name}: {left_img.size}\n"
                f"{right_file.name}: {right_img.size}"
            )

        w, h = left_img.size

        # Create combined frame: left image + right image
        combined = Image.new("RGBA", (w * 2, h))
        combined.paste(left_img, (0, 0))
        combined.paste(right_img, (w, 0))

        frames.append(combined)

    combined_size = frames[0].size
    for i, frame in enumerate(frames):
        if frame.size != combined_size:
            raise ValueError(
                f"All combined frames must have same size. "
                f"Frame 0: {combined_size}, frame {i}: {frame.size}"
            )

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
    print(f"Frames: {len(frames)}")
    print(f"Combined frame size: {combined_size}")


pngs_side_by_side_to_webp(
    left_dir="/Users/aljoscha/Desktop/zap_no_segs",
    right_dir="/Users/aljoscha/Desktop/zap_segs",
    output_webp="/Users/aljoscha/Desktop/output_side_by_side.webp",
    fps=1,
    crop_left=0,
    crop_top=300,
    crop_right=1200,
    crop_bottom=100,
)