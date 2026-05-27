
import os
from PIL import Image, ImageChops

# Configuration
source_dir = os.path.join(os.getcwd(), 'ideal')
output_dir = os.path.join(source_dir, 'resized')
resize_width = 650  # Desired width in pixels
resize_height = 800  # Desired height in pixels

required_padding = 20
white = (255, 255, 255)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)


# Helper function to check if an image has white padding
def has_white_padding(img, padding=10):
    w, h = img.size
    border = {
        "top": img.crop((0, 0, w, padding)),
        "bottom": img.crop((0, h - padding, w, h)),
        "left": img.crop((0, 0, padding, h)),
        "right": img.crop((w - padding, 0, w, h)),
    }
    for part in border.values():
        bg = Image.new("RGB", part.size, white)
        if ImageChops.difference(part, bg).getbbox():
            return False
    return True

# Supported image extensions
image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')

# Iterate over files in the source directory
for filename in os.listdir(source_dir):
    if filename.lower().endswith(image_extensions):
        source_path = os.path.join(source_dir, filename)
        output_path = os.path.join(output_dir, filename)

        try:
            with Image.open(source_path) as img:
                img = img.convert("RGB")  # Ensure it's in RGB mode
                resized_img = img.resize((resize_width, resize_height), Image.Resampling.LANCZOS)

                if not has_white_padding(resized_img, required_padding):
                    new_size = (
                        resized_img.width + 2 * required_padding,
                        resized_img.height + 2 * required_padding
                    )
                    padded_img = Image.new("RGB", new_size, white)
                    padded_img.paste(resized_img, (required_padding, required_padding))
                else:
                    padded_img = resized_img

                padded_img.save(output_path)
                print(f"Processed and saved: {output_path}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")


# img_path = "C:\Users\Anik.Mishu\PycharmProjects\ImgProcessor\cards-smart-city-applications"
#img = "C:\Users\Anik.Mishu\OneDrive - Adastra, s.r.o\Desktop\Artifactz\Artifactz BD\img\cards-smart-city-applications\card-smart-traffic.png"
#imgs = os.listdir("./cards-smart-city-applications")
#print(imgs)
#img = Image.open("./cards-smart-city-applications/card-smart-traffic.png")
#print(img.size)
#reduced_size = (int(img.size[0] * 0.6), int(img.size[1] * 0.6))
#print(reduced_size)
#reduced_img = img.resize(reduced_size, Image.Resampling.LANCZOS)
#print(reduced_img.size)
#reduced_img.save('test.png')