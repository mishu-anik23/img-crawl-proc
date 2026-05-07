#!/usr/bin/env python3
"""
Image Processor for ShatkahonEU Punjabi Images
Processes images and extracts metadata
"""

import os
import re
import argparse
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from datetime import datetime


class ImageProcessor:
    """Process images and extract metadata"""
    
    PRODUCT_PREFIX = "SKEU"
    PRODUCT_NAME = "Panjabi"
    
    def __init__(self, image_dir):
        self.image_dir = Path(image_dir)
        self.processed_dir = self.image_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        self.metadata = []
    
    def parse_filename(self, filename):
        """
        Parse filename to extract product info
        Format: Panjabi (Ps-A90)-image-1.jpg
        Returns: {product_name, product_code, slug, original_name}
        """
        # Remove extension
        name_no_ext = filename.rsplit('.', 1)[0]
        
        # Pattern: ProductName (CODE)-image-NUMBER
        pattern = r'(\w+)\s*\(([A-Za-z]+-[A-Za-z0-9]+)\)-image-(\d+)'
        match = re.match(pattern, name_no_ext)
        
        if not match:
            return None
        
        product_name_raw = match.group(1)  # e.g., "Panjabi"
        code_raw = match.group(2)           # e.g., "Ps-A90"
        image_num = match.group(3)          # e.g., "1"
        
        # Extract code parts
        code_parts = code_raw.split('-')
        if len(code_parts) == 2:
            code_prefix = code_parts[0].upper()  # PS
            code_number = code_parts[1].upper()  # A90
        else:
            return None
        
        # Format product name: Panjabi-PS-A90
        product_name = f"{product_name_raw}-{code_prefix}-{code_number}"
        
        # Format product code: SKEU-PS-A90
        product_code = f"{self.PRODUCT_PREFIX}-{code_prefix}-{code_number}"
        
        # Create URL-friendly slug
        slug = f"{product_name_raw.lower()}-{code_prefix.lower()}-{code_number.lower()}-image-{image_num}"
        
        return {
            'product_name': product_name,
            'product_code': product_code,
            'slug': slug,
            'original_name': filename,
            'image_num': image_num
        }
    
    def crop_black_pixels(self, img):
        """
        Remove black pixels from bottom of image
        Returns: cropped image
        """
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        
        # Find rows that are mostly black (sum of RGB channels < threshold)
        # We look from bottom to top
        black_threshold = 30  # Pixels with RGB sum < 30 are considered black
        height = img_array.shape[0]
        
        # Calculate brightness for each row
        row_brightness = np.mean(img_array, axis=(1, 2))
        
        # Find the bottom row that's not black
        crop_bottom = height
        for i in range(height - 80, -80, -80):
            if row_brightness[i] > black_threshold:
                crop_bottom = i + 1
                break
        
        # Crop the image
        return img.crop((0, 0, img_array.shape[1], crop_bottom))
    
    def optimize_image(self, img_path):
        """
        Process image: crop black pixels, optimize resolution
        Returns: processed PIL Image
        """
        img = Image.open(img_path)
        
        # Crop black pixels from bottom
        img = self.crop_black_pixels(img)
        
        # Optimize resolution - if image is very large, reduce it
        width, height = img.size
        max_width = 1920
        max_height = 1200
        
        if width > max_width or height > max_height:
            # Calculate scaling factor
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def process_images(self, generate_excel=False):
        """
        Process all images in directory
        """
        if not self.image_dir.exists():
            print(f"Error: Directory {self.image_dir} not found")
            return False
        
        image_files = sorted([f for f in os.listdir(self.image_dir) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))])
        
        if not image_files:
            print(f"No images found in {self.image_dir}")
            return False
        
        print(f"Found {len(image_files)} images")
        print("Processing images...")
        
        for idx, filename in enumerate(image_files, 1):
            try:
                # Parse filename
                metadata = self.parse_filename(filename)
                if not metadata:
                    print(f"⚠ Skipped: {filename} (couldn't parse)")
                    continue
                
                img_path = self.image_dir / filename
                
                # Process image
                processed_img = self.optimize_image(img_path)
                
                # Save processed image
                file_ext = Path(filename).suffix
                output_filename = f"{metadata['slug']}{file_ext}"
                output_path = self.processed_dir / output_filename
                
                processed_img.save(output_path, quality=95)
                
                # Store metadata
                metadata['output_filename'] = output_filename
                self.metadata.append(metadata)
                
                print(f"✓ [{idx}/{len(image_files)}] {filename} -> {output_filename}")
                
            except Exception as e:
                print(f"✗ Error processing {filename}: {str(e)}")
        
        print(f"\n✓ Processed {len(self.metadata)} images")
        
        if generate_excel:
            self.generate_excel()
        
        return True
    
    def generate_excel(self):
        """Generate Excel file with metadata"""
        if not self.metadata:
            print("No metadata to export")
            return False
        
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Image Metadata"
            
            # Add headers
            headers = ['Product Name', 'Product Code', 'Image Slug']
            ws.append(headers)
            
            # Add data
            for item in self.metadata:
                ws.append([
                    item['product_name'],
                    item['product_code'],
                    item['slug']
                ])
            
            # Adjust column widths
            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 25
            ws.column_dimensions['C'].width = 35
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            excel_filename = f"image_metadata_{timestamp}.xlsx"
            excel_path = self.image_dir / excel_filename
            
            wb.save(excel_path)
            print(f"✓ Excel file created: {excel_filename}")
            return True
            
        except Exception as e:
            print(f"✗ Error generating Excel: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Process images and extract metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_processor.py "C:\\path\\to\\images"
  python image_processor.py "C:\\path\\to\\images" -f
        """
    )
    
    parser.add_argument('image_path', 
                       help='Path to image directory')
    parser.add_argument('-f', '--excel', 
                       action='store_true',
                       help='Generate Excel file with metadata')
    
    args = parser.parse_args()
    
    # Process images
    processor = ImageProcessor(args.image_path)
    success = processor.process_images(generate_excel=args.excel)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
