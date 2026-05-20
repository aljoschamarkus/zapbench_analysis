from PIL import Image
from pathlib import Path


def combine_two_images_side_by_side(
    left_path,
    right_path,
    output_path,
    crop_left=0,
    crop_top=0,
    crop_right=0,
    crop_bottom=0,
):
    left_img = Image.open(left_path).convert("RGBA")
    right_img = Image.open(right_path).convert("RGBA")

    lw, lh = left_img.size
    rw, rh = right_img.size

    # Crop both images equally
    left_img = left_img.crop((crop_left, crop_top, lw - crop_right, lh - crop_bottom))
    right_img = right_img.crop((crop_left, crop_top, rw - crop_right, rh - crop_bottom))

    if left_img.size != right_img.size:
        raise ValueError(
            f"Cropped images must have same size.\n"
            f"Left: {left_img.size}, Right: {right_img.size}"
        )

    w, h = left_img.size

    # Create combined image
    combined = Image.new("RGBA", (w * 2, h))
    combined.paste(left_img, (0, 0))
    combined.paste(right_img, (w, 0))

    combined.save(output_path)

    print(f"Saved: {output_path}")
    print(f"Final size: {combined.size}")


# Example usage
combine_two_images_side_by_side(
    left_path="/Users/aljoscha/Desktop/mask.png",
    right_path="/Users/aljoscha/Desktop/mask_out.png",
    output_path="/Users/aljoscha/Desktop/merge.png",
    crop_left=0,
    crop_top=0,
    crop_right=0,
    crop_bottom=0,
)