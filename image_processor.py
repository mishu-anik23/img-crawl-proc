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
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from datetime import datetime


class ImageProcessor:
    """Process images and extract metadata"""
    
    PRODUCT_PREFIX = "SKEU"
    PRODUCT_NAME = "Panjabi"
    DATA_FILENAMES = ["sku_punjabi_price.xlsx", "skeu-punjabi-price.xlsx"]
    CONTACT_NUMBER = "+4917673953530"
    DEFAULT_LOGO_TEXT = "Shatkahon EU"
    
    def __init__(self, image_dir, data_path=None, logo_path=None):
        self.image_dir = Path(image_dir)
        self.processed_dir = self.image_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        self.metadata = []
        self.pricing = {}
        self.data_path = Path(data_path) if data_path else None
        self.logo_path = Path(logo_path) if logo_path else None
    
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
    
    def normalize_lookup_key(self, value):
        return re.sub(r'[^A-Z0-9]', '', str(value).upper())
    
    def load_pricing_data(self):
        if self.pricing:
            return True
        search_paths = []
        if self.data_path:
            search_paths.append(self.data_path)
        for filename in self.DATA_FILENAMES:
            search_paths.extend([
                self.image_dir / filename,
                self.image_dir.parent / filename,
                Path.cwd() / filename,
            ])
        data_file = None
        for candidate in search_paths:
            if candidate and Path(candidate).exists():
                data_file = Path(candidate)
                break
        if not data_file:
            return False
        try:
            wb = load_workbook(data_file, data_only=True)
            ws = wb.active
            header = [str(cell.value).strip() if cell.value and str(cell.value).strip() else "" for cell in next(ws.iter_rows(min_row=1, max_row=1))]
            sku_idx = None
            price_idx = None
            for i, heading in enumerate(header):
                if heading and sku_idx is None and re.search(r'sku|product.*code|product.*sku|code', heading, re.I):
                    sku_idx = i
                if heading and price_idx is None and re.search(r'sell.*price|price|cost', heading, re.I):
                    price_idx = i
            if sku_idx is None and len(header) >= 1:
                sku_idx = 0
            if price_idx is None and len(header) >= 2:
                price_idx = 1
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row or sku_idx >= len(row) or row[sku_idx] is None:
                    continue
                raw_sku = str(row[sku_idx]).strip()
                raw_price = row[price_idx] if price_idx < len(row) else None
                if not raw_sku or raw_price is None:
                    continue
                self.pricing[self.normalize_lookup_key(raw_sku)] = raw_price
            return bool(self.pricing)
        except Exception as e:
            print(f"✗ Error loading price data from {data_file}: {e}")
            return False
    
    def get_image_price(self, metadata):
        if not self.pricing:
            return None
        candidates = [
            metadata.get('product_code'),
            metadata.get('product_name'),
            metadata.get('slug'),
            metadata.get('product_code', '').replace('SKEU-', ''),
            metadata.get('product_code', '').replace('-', ''),
            metadata.get('product_name', '').replace('-', ''),
        ]
        for candidate in candidates:
            if candidate:
                key = self.normalize_lookup_key(candidate)
                if key in self.pricing:
                    return self.pricing[key]
        code_tail = metadata.get('product_code', '').split('-')[-1]
        if code_tail:
            key = self.normalize_lookup_key(code_tail)
            if key in self.pricing:
                return self.pricing[key]
        return None
    
    def find_logo_path(self):
        if self.logo_path and self.logo_path.exists():
            return self.logo_path
        candidates = []
        if self.image_dir.exists():
            candidates.extend(self.image_dir.glob('*logo-shatkahonEU-small*'))
            candidates.extend(self.image_dir.glob('*shatkahon*'))
            candidates.extend(self.image_dir.glob('*Shatkahon*'))
        parent_dir = self.image_dir.parent
        if parent_dir.exists():
            candidates.extend(parent_dir.glob('*logo-shatkahonEU-small*'))
            candidates.extend(parent_dir.glob('*shatkahon*'))
            candidates.extend(parent_dir.glob('*Shatkahon*'))
        brand_logo_dir = Path.cwd() / 'brand-logo'
        if brand_logo_dir.exists():
            candidates.extend(brand_logo_dir.glob('*logo-shatkahonEU-small*'))
            candidates.extend(brand_logo_dir.glob('*shatkahon*'))
            candidates.extend(brand_logo_dir.glob('*ShatkahonEU*'))
        root_candidates = Path.cwd().glob('*logo-shatkahonEU-small*')
        candidates.extend(root_candidates)
        shatkahon_root = Path.cwd() / 'ShatkahonEU' / 'logo-satkahonEU-small.png'
        if shatkahon_root.exists():
            candidates.append(shatkahon_root)
        for candidate in candidates:
            if candidate.is_file() and candidate.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
                return candidate
        return None
    
    def add_bottom_bar(self, img, metadata):
        width, height = img.size
        bar_height = max(100, int(width * 0.14))
        new_image = Image.new('RGB', (width, height + bar_height), 'white')
        new_image.paste(img, (0, 0))
        draw = ImageDraw.Draw(new_image)
        try:
            font_size = max(18, int(bar_height * 0.28))
            font = ImageFont.truetype('arial.ttf', font_size)
        except Exception:
            font = ImageFont.load_default()
        logo_path = self.find_logo_path()
        left_padding = 20
        text_padding = 20
        logo_width = 0
        if logo_path:
            try:
                logo_img = Image.open(logo_path)
                if logo_img.mode not in ('RGBA', 'LA'):
                    logo_img = logo_img.convert('RGBA')
                logo_img.thumbnail((int(width * 0.22), bar_height - 20), Image.Resampling.LANCZOS)
                logo_x = left_padding
                logo_y = height + (bar_height - logo_img.height) // 2
                new_image.paste(logo_img, (logo_x, logo_y), logo_img)
                logo_width = logo_img.width + text_padding
            except Exception:
                logo_width = 0
        else:
            title_text = self.DEFAULT_LOGO_TEXT
            text_size = draw.textbbox((0, 0), title_text, font=font)
            title_y = height + (bar_height - (text_size[3] - text_size[1])) // 2
            draw.text((left_padding, title_y), title_text, fill='black', font=font)
            logo_width = 0
        text_x = left_padding + logo_width
        price_value = self.get_image_price(metadata)
        if price_value is None:
            price_line = 'Sell price: N/A'
        else:
            raw_price = str(price_value).strip()
            if raw_price.startswith('€'):
                raw_price = raw_price.lstrip('€ ').strip()
            price_line = f'Sell price: €{raw_price}'
        sku_text = metadata.get('product_code', '')
        contact_text = self.CONTACT_NUMBER
        line_spacing = 8
        sku_size = draw.textbbox((0, 0), sku_text, font=font)
        price_size = draw.textbbox((0, 0), price_line, font=font)
        text_total_height = (sku_size[3] - sku_size[1]) + (price_size[3] - price_size[1]) + line_spacing
        text_y = height + (bar_height - text_total_height) // 2
        draw.text((text_x, text_y), sku_text, fill='black', font=font)
        draw.text((text_x, text_y + (sku_size[3] - sku_size[1]) + line_spacing), price_line, fill='black', font=font)
        contact_size = draw.textbbox((0, 0), contact_text, font=font)
        contact_x = width - left_padding - (contact_size[2] - contact_size[0])
        contact_y = height + (bar_height - (contact_size[3] - contact_size[1])) // 2
        draw.text((contact_x, contact_y), contact_text, fill='black', font=font)
        metadata['price'] = price_line
        metadata['contact'] = contact_text
        return new_image
    
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
        if not self.load_pricing_data():
            print(f"⚠ Warning: Could not find any of {self.DATA_FILENAMES}. Price labels will be shown as N/A.")
        
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
                processed_img = self.add_bottom_bar(processed_img, metadata)
                
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
            headers = ['Product Name', 'Product Code', 'Image Slug', 'Sell Price']
            ws.append(headers)
            
            # Add data
            for item in self.metadata:
                ws.append([
                    item['product_name'],
                    item['product_code'],
                    item['slug'],
                    item.get('price', '')
                ])
            
            # Adjust column widths
            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 25
            ws.column_dimensions['C'].width = 35
            ws.column_dimensions['D'].width = 18
            
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
    parser.add_argument('-d', '--data',
                       help='Path to the SKU pricing Excel file (sku_punjabi_price.xlsx)')
    parser.add_argument('-l', '--logo',
                       help='Path to the Shatkahon EU logo image to print in the footer')
    
    args = parser.parse_args()
    
    # Process images
    processor = ImageProcessor(args.image_path, data_path=args.data, logo_path=args.logo)
    success = processor.process_images(generate_excel=args.excel)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
