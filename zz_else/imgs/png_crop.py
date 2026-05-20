from PIL import Image

def crop_png(input_path, output_path,
             crop_left=0, crop_top=0,
             crop_right=0, crop_bottom=0):
    img = Image.open(input_path)
    w, h = img.size

    cropped = img.crop((
        crop_left,
        crop_top,
        w - crop_right,
        h - crop_bottom
    ))

    cropped.save(output_path, dpi=(1000, 1000))
    print(f"Saved: {output_path}")


# Example
crop_png(
    input_path='/Users/aljoscha/Desktop/Bildschirmfoto 2026-05-19 um 14.38.32.png',
    output_path="/Users/aljoscha/Desktop/mask_out.png",
    crop_left=1000,
    crop_top=610,
    crop_right=1100,
    crop_bottom=350
)