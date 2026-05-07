# Image Processor for ShatkahonEU Punjabi Images

A Python utility to process images and extract metadata for URL-compatible slugs and product information.

## Features

✓ **Filename Parsing**: Automatically extracts product information from image filenames
✓ **Image Optimization**: 
  - Removes black pixels from bottom of images
  - Optimizes resolution for web use (max 1920x1200)
  - Preserves quality with 95% JPEG quality

✓ **URL-Compatible Naming**: Converts filenames to slug format (lowercase, hyphenated)
✓ **Product Code Generation**: Automatically adds "SKEU" prefix to product codes
✓ **Batch Processing**: Processes all images in a directory
✓ **Excel Export**: Optional metadata export to Excel file

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Processing (without Excel)
```bash
python image_processor.py "C:\path\to\images"
```

### Processing with Excel Export
```bash
python image_processor.py "C:\path\to\images" -f
```

## Filename Format

Input filenames must follow this pattern:
```
ProductName (Code-Number)-image-ImageNum.jpg
```

### Example:
- Input: `Panjabi (Ps-A90)-image-1.jpg`
- Product Name: `Panjabi-PS-A90`
- Product Code: `SKEU-PS-A90`
- Image Slug: `panjabi-ps-a90-image-1`
- Output: `panjabi-ps-a90-image-1.jpg` (in `processed/` folder)

## Output

### Processed Images
- Location: `{original_dir}/processed/`
- Format: URL-friendly slug names in lowercase with hyphens
- Quality: Optimized resolution with black pixels removed from bottom

### Excel File (optional)
- Location: `{original_dir}/image_metadata_YYYYMMDD_HHMMSS.xlsx`
- Columns:
  - **Product Name**: e.g., `Panjabi-PS-A90`
  - **Product Code**: e.g., `SKEU-PS-A90`
  - **Image Slug**: e.g., `panjabi-ps-a90-image-1`

## Example Run

```bash
$ python image_processor.py "ShatkahonEU\Punjabi" -f
Found 31 images
Processing images...
✓ [1/31] Panjabi (Ps-A89)-image-1.jpg -> panjabi-ps-a89-image-1.jpg
✓ [2/31] Panjabi (Ps-A90)-image-1.jpg -> panjabi-ps-a90-image-1.jpg
...
✓ Processed 31 images
✓ Excel file created: image_metadata_20260506_224052.xlsx
```

## Requirements

- Python 3.7+
- Pillow (PIL) - Image processing
- NumPy - Array handling
- openpyxl - Excel file creation

## How It Works

1. **Scans** the input directory for image files (.jpg, .jpeg, .png, .bmp)
2. **Parses** each filename to extract product information
3. **Processes** each image:
   - Removes black text/pixels from the bottom
   - Optimizes resolution if larger than 1920x1200
   - Maintains 95% JPEG quality
4. **Saves** processed images with URL-friendly names
5. **Optionally exports** metadata to Excel file

## Notes

- Original images remain unchanged
- Processed images are saved in a `processed` subfolder
- Black pixel removal uses adaptive threshold (RGB brightness < 30)
- Files that cannot be parsed are skipped with a warning
- Excel file includes timestamp in filename for uniqueness
