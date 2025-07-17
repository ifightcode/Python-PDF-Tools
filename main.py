import pymupdf as fitz  # PyMuPDF
import os
from PIL import Image
import io
import glob
import argparse
import sys
import re

def extract_images_from_pdf(pdf_path, output_folder="extracted_images"):
    """
    Extract all images from a PDF file and save them to a specified folder.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_folder (str): Folder to save extracted images
    
    Returns:
        int: Number of images extracted
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    image_count = 0
    
    # Get the base name of the PDF file (without extension)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # Iterate through each page
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        
        # Get list of images on the page
        image_list = page.get_images(full=True)
        
        # Extract each image
        for img_index, img in enumerate(image_list):
            # Get image data
            xref = img[0]
            pix = fitz.Pixmap(pdf_document, xref)
            
            # Skip if image is a mask
            if pix.n - pix.alpha < 4:  # GRAY or RGB
                # Generate filename
                img_filename = f"{pdf_name}_page{page_num + 1}_img{img_index + 1}.png"
                img_path = os.path.join(output_folder, img_filename)
                
                # Save image
                if pix.n - pix.alpha == 1:  # Grayscale
                    pix.save(img_path)
                else:  # RGB
                    pix.save(img_path)
                
                image_count += 1
                print(f"Extracted: {img_filename}")
            
            # Alternative method using PIL for better format handling
            else:
                # Convert to RGB if CMYK
                if pix.n == 5:  # CMYK + alpha
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                img_filename = f"{pdf_name}_page{page_num + 1}_img{img_index + 1}.png"
                img_path = os.path.join(output_folder, img_filename)
                pix.save(img_path)
                image_count += 1
                print(f"Extracted: {img_filename}")
            
            # Clean up
            pix = None
    
    # Close the PDF
    pdf_document.close()
    
    return image_count

def extract_images_with_quality_filter(pdf_path, output_folder="extracted_images", min_width=100, min_height=100):
    """
    Extract images from PDF with quality filtering (minimum dimensions).
    
    Args:
        pdf_path (str): Path to the PDF file
        output_folder (str): Folder to save extracted images
        min_width (int): Minimum image width
        min_height (int): Minimum image height
    
    Returns:
        int: Number of images extracted
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    pdf_document = fitz.open(pdf_path)
    image_count = 0
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            pix = fitz.Pixmap(pdf_document, xref)
            
            # Check image dimensions
            if pix.width >= min_width and pix.height >= min_height:
                # Handle different color spaces
                if pix.n - pix.alpha == 4:  # CMYK
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                
                img_filename = f"{pdf_name}_page{page_num + 1}_img{img_index + 1}.png"
                img_path = os.path.join(output_folder, img_filename)
                pix.save(img_path)
                
                image_count += 1
                print(f"Extracted: {img_filename} ({pix.width}x{pix.height})")
            else:
                print(f"Skipped small image: {pix.width}x{pix.height} (minimum: {min_width}x{min_height})")
            
            pix = None
    
    pdf_document.close()
    return image_count

def rotate_images_in_directory(directory_path, direction="anticlockwise", overwrite=True):
    """
    Rotate all images in a directory clockwise or anticlockwise by 90 degrees.
    
    Args:
        directory_path (str): Path to directory containing images
        direction (str): "clockwise" or "anticlockwise" (default: "anticlockwise")
        overwrite (bool): Whether to overwrite original files or create new ones
    
    Returns:
        int: Number of images rotated
    """
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return 0
    
    # Determine rotation angle based on direction
    if direction.lower() in ["clockwise", "cw"]:
        angle = -90  # Negative for clockwise
        direction_text = "clockwise"
    elif direction.lower() in ["anticlockwise", "counterclockwise", "acw", "ccw"]:
        angle = 90   # Positive for anticlockwise
        direction_text = "anticlockwise"
    else:
        print(f"Invalid direction: {direction}. Use 'clockwise' or 'anticlockwise'")
        return 0
    
    # Supported image formats
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff', '*.webp']
    image_files = []
    
    # Find all image files in directory
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory_path, extension)))
        image_files.extend(glob.glob(os.path.join(directory_path, extension.upper())))
    
    if not image_files:
        print(f"No image files found in: {directory_path}")
        return 0
    
    print(f"Rotating {len(image_files)} images {direction_text} by 90 degrees...")
    rotated_count = 0
    
    for image_path in image_files:
        try:
            # Open image
            with Image.open(image_path) as img:
                # Rotate image
                rotated_img = img.rotate(angle, expand=True)
                
                # Save rotated image
                if overwrite:
                    rotated_img.save(image_path)
                    print(f"Rotated {direction_text}: {os.path.basename(image_path)}")
                else:
                    # Create new filename with rotation suffix
                    name, ext = os.path.splitext(image_path)
                    new_path = f"{name}_rotated_{direction_text}{ext}"
                    rotated_img.save(new_path)
                    print(f"Rotated {direction_text} and saved as: {os.path.basename(new_path)}")
                
                rotated_count += 1
                
        except Exception as e:
            print(f"Error rotating {os.path.basename(image_path)}: {str(e)}")
    
    return rotated_count

def create_pdf_from_images(directory_path, output_pdf=None):
    """
    Create a PDF from images in a directory, following page numbering convention.
    Looks for files with pattern *_page{N}_*.png and orders them by page number.
    
    Args:
        directory_path (str): Path to directory containing images
        output_pdf (str): Output PDF filename (optional, auto-generated if None)
    
    Returns:
        str: Path to created PDF file, or None if failed
    """
    if not os.path.exists(directory_path):
        print(f"Directory not found: {directory_path}")
        return None
    
    # Find all image files in directory
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff', '*.webp']
    image_files = []
    
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory_path, extension)))
        image_files.extend(glob.glob(os.path.join(directory_path, extension.upper())))
    
    if not image_files:
        print(f"No image files found in: {directory_path}")
        return None
    
    # Extract page numbers and sort images by page number
    page_images = []
    page_pattern = re.compile(r'.*_page(\d+)_.*\.(png|jpg|jpeg|gif|bmp|tiff|webp)$', re.IGNORECASE)
    
    for image_path in image_files:
        filename = os.path.basename(image_path)
        match = page_pattern.match(filename)
        
        if match:
            page_num = int(match.group(1))
            page_images.append((page_num, image_path))
        else:
            print(f"Warning: Skipping file (doesn't match page pattern): {filename}")
    
    if not page_images:
        print("No images found matching the page numbering pattern (*_page{N}_*.ext)")
        print("Expected pattern: filename_page1_something.png, filename_page2_something.jpg, etc.")
        return None
    
    # Sort by page number
    page_images.sort(key=lambda x: x[0])
    
    # Generate output PDF name if not provided
    if output_pdf is None:
        dir_name = os.path.basename(directory_path.rstrip('/\\'))
        output_pdf = f"{dir_name}_combined.pdf"
    
    # Ensure output PDF has .pdf extension
    if not output_pdf.lower().endswith('.pdf'):
        output_pdf += '.pdf'
    
    print(f"Creating PDF from {len(page_images)} images...")
    print(f"Page range: {page_images[0][0]} to {page_images[-1][0]}")
    
    try:
        # Create new PDF document
        pdf_document = fitz.open()
        
        for page_num, image_path in page_images:
            try:
                # Open image with PIL to ensure compatibility
                with Image.open(image_path) as img:
                    # Convert to RGB if necessary (for JPEG compatibility)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Save image to bytes
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    # Get image dimensions
                    img_width, img_height = img.size
                    
                    # Create PDF page with image dimensions (in points, 72 DPI)
                    # Convert pixels to points (assuming 72 DPI)
                    page_width = img_width * 72 / 96  # Assuming 96 DPI for screen
                    page_height = img_height * 72 / 96
                    
                    # Create new page
                    page = pdf_document.new_page(width=page_width, height=page_height)
                    
                    # Insert image to fill the entire page
                    page.insert_image(fitz.Rect(0, 0, page_width, page_height), stream=img_bytes.getvalue())
                    
                    print(f"Added page {page_num}: {os.path.basename(image_path)}")
                    
            except Exception as e:
                print(f"Error processing image {os.path.basename(image_path)}: {str(e)}")
                continue
        
        if pdf_document.page_count == 0:
            print("No pages were successfully added to the PDF")
            pdf_document.close()
            return None
        
        # Save PDF
        pdf_document.save(output_pdf)
        pdf_document.close()
        
        print(f"\nPDF created successfully: {output_pdf}")
        print(f"Total pages: {len(page_images)}")
        
        return output_pdf
        
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        return None

def compress_pdf(input_pdf, output_pdf=None, compression_level="medium"):
    """
    Compress a PDF file to reduce its size.
    
    Args:
        input_pdf (str): Path to input PDF file
        output_pdf (str): Path to output PDF file (optional, auto-generated if None)
        compression_level (str): Compression level - "low", "medium", "high" (default: "medium")
    
    Returns:
        str: Path to compressed PDF file, or None if failed
    """
    if not os.path.exists(input_pdf):
        print(f"PDF file not found: {input_pdf}")
        return None
    
    # Generate output PDF name if not provided
    if output_pdf is None:
        name, ext = os.path.splitext(input_pdf)
        output_pdf = f"{name}_compressed{ext}"
    
    # Ensure output PDF has .pdf extension
    if not output_pdf.lower().endswith('.pdf'):
        output_pdf += '.pdf'
    
    # Set compression parameters based on level
    compression_settings = {
        "low": {
            "garbage": 1,
            "clean": True
        },
        "medium": {
            "deflate": True,
            "garbage": 2,
            "clean": True
        },
        "high": {
            "deflate": True,
            "garbage": 4,
            "clean": True,
            "pretty": True
        }
    }
    
    if compression_level not in compression_settings:
        print(f"Invalid compression level: {compression_level}. Use 'low', 'medium', or 'high'")
        return None
    
    try:
        # Get original file size
        original_size = os.path.getsize(input_pdf)
        print(f"Original PDF size: {original_size / (1024*1024):.2f} MB")
        
        # Open the PDF
        pdf_document = fitz.open(input_pdf)
        
        # Apply compression settings
        settings = compression_settings[compression_level]
        
        print(f"Compressing PDF with {compression_level} compression...")
        
        # Save with compression
        pdf_document.save(
            output_pdf,
            **settings
        )
        
        pdf_document.close()
        
        # Get compressed file size
        compressed_size = os.path.getsize(output_pdf)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Compressed PDF size: {compressed_size / (1024*1024):.2f} MB")
        print(f"Compression ratio: {compression_ratio:.1f}% reduction")
        print(f"Compressed PDF saved as: {output_pdf}")
        
        return output_pdf
        
    except Exception as e:
        print(f"Error compressing PDF: {str(e)}")
        return None

def compress_pdf_advanced(input_pdf, output_pdf=None, image_quality=30, max_width=1200, max_height=1600):
    """
    Advanced PDF compression using aggressive image optimization and page rendering.
    
    This method renders each PDF page as an image, then compresses it heavily.
    Best for image-heavy PDFs where maximum compression is needed.
    
    Args:
        input_pdf (str): Path to input PDF file
        output_pdf (str): Path to output PDF file (optional, auto-generated if None)
        image_quality (int): JPEG quality for rendered pages (1-100, default: 30)
        max_width (int): Maximum width for rendered pages (default: 1200)
        max_height (int): Maximum height for rendered pages (default: 1600)
    
    Returns:
        str: Path to compressed PDF file, or None if failed
    """
    if not os.path.exists(input_pdf):
        print(f"PDF file not found: {input_pdf}")
        return None
    
    # Generate output PDF name if not provided
    if output_pdf is None:
        name, ext = os.path.splitext(input_pdf)
        output_pdf = f"{name}_advanced_compressed{ext}"
    
    # Ensure output PDF has .pdf extension
    if not output_pdf.lower().endswith('.pdf'):
        output_pdf += '.pdf'
    
    try:
        # Get original file size
        original_size = os.path.getsize(input_pdf)
        print(f"Original PDF size: {original_size / (1024*1024):.2f} MB")
        print(f"Advanced compression settings: Quality={image_quality}%, Max size={max_width}x{max_height}")
        
        # Open the PDF
        pdf_document = fitz.open(input_pdf)
        
        # Create new PDF document for output
        new_pdf = fitz.open()
        
        print("Rendering pages as compressed images...")
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            
            # Calculate optimal resolution
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Calculate scale factor to fit within max dimensions
            scale_x = max_width / page_width if page_width > max_width else 1.0
            scale_y = max_height / page_height if page_height > max_height else 1.0
            scale = min(scale_x, scale_y, 2.0)  # Cap at 2x for quality
            
            # Create transformation matrix
            mat = fitz.Matrix(scale, scale)
            
            # Render page as image
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PIL Image for better compression
            img_data = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Convert to RGB if necessary
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                pil_image = pil_image.convert('RGB')
            
            # Apply additional optimizations
            # 1. Reduce colors for non-photographic content
            if image_quality < 50:
                # Quantize colors for very low quality settings
                pil_image = pil_image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                pil_image = pil_image.convert('RGB')
            
            # 2. Apply slight blur to reduce JPEG artifacts at low quality
            if image_quality < 40:
                from PIL import ImageFilter
                pil_image = pil_image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Compress image aggressively
            img_bytes = io.BytesIO()
            
            # Use progressive JPEG for better compression
            pil_image.save(
                img_bytes, 
                format='JPEG', 
                quality=image_quality,
                optimize=True,
                progressive=True,
                subsampling=2 if image_quality < 50 else 0  # Aggressive chroma subsampling for low quality
            )
            
            img_bytes.seek(0)
            
            # Calculate new page dimensions
            new_width = pil_image.width * 72 / 96  # Convert to points
            new_height = pil_image.height * 72 / 96
            
            # Create new page and insert compressed image
            new_page = new_pdf.new_page(width=new_width, height=new_height)
            new_page.insert_image(fitz.Rect(0, 0, new_width, new_height), stream=img_bytes.getvalue())
            
            # Clean up
            pix = None
            
            print(f"Processed page {page_num + 1}/{pdf_document.page_count} - Size: {len(img_bytes.getvalue()) / 1024:.1f} KB")
        
        # Save with maximum compression settings
        new_pdf.save(
            output_pdf,
            deflate=True,
            garbage=4,
            clean=True,
            pretty=True
        )
        
        new_pdf.close()
        pdf_document.close()
        
        # Get compressed file size
        compressed_size = os.path.getsize(output_pdf)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"Compressed PDF size: {compressed_size / (1024*1024):.2f} MB")
        print(f"Compression ratio: {compression_ratio:.1f}% reduction")
        print(f"Advanced compressed PDF saved as: {output_pdf}")
        
        return output_pdf
        
    except Exception as e:
        print(f"Error in advanced compression: {str(e)}")
        return None

def show_help():
    """Display detailed help information for all commands."""
    help_text = """
PDF Tools - Comprehensive PDF Processing Utility

COMMANDS:
  extract       Extract images from PDF files
  rotate        Rotate images in a directory
  create_pdf    Create PDF from images with page numbering
  compress      Basic PDF compression
  compress_adv  Advanced PDF compression with image optimization
  help          Show this detailed help

═══════════════════════════════════════════════════════════════════════════════

EXTRACT - Extract images from PDF files
  Usage: python main.py extract <pdf_file> [options]
  
  Options:
    --min-width INT     Minimum image width to extract (default: 50)
    --min-height INT    Minimum image height to extract (default: 50)
  
  Examples:
    python main.py extract document.pdf
    python main.py extract document.pdf --min-width 100 --min-height 100
  
  Output: Creates folder named {pdf_name}_images with extracted images

═══════════════════════════════════════════════════════════════════════════════

ROTATE - Rotate images in a directory
  Usage: python main.py rotate <directory> [options]
  
  Options:
    --direction, -d     Rotation direction: clockwise, anticlockwise, cw, acw
    --no-overwrite      Create new files instead of overwriting originals
  
  Examples:
    python main.py rotate image_folder
    python main.py rotate image_folder --direction clockwise
    python main.py rotate image_folder -d cw --no-overwrite
  
  Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP

═══════════════════════════════════════════════════════════════════════════════

CREATE_PDF - Create PDF from images with page numbering
  Usage: python main.py create_pdf <directory> [options]
  
  Options:
    --output, -o FILE   Output PDF filename
  
  Examples:
    python main.py create_pdf image_folder
    python main.py create_pdf image_folder --output my_document.pdf
  
  Image naming convention: *_page{N}_*.ext
  Example: deed_page1_img1.png, contract_page2_scan.jpg

═══════════════════════════════════════════════════════════════════════════════

COMPRESS - Basic PDF compression
  Usage: python main.py compress <pdf_file> [options]
  
  Options:
    --compression, -c   Compression level: low, medium, high (default: medium)
    --output, -o FILE   Output PDF filename
  
  Examples:
    python main.py compress large_file.pdf
    python main.py compress large_file.pdf --compression high
    python main.py compress large_file.pdf -c high -o small_file.pdf
  
  Compression levels:
    low     - Basic compression, fastest
    medium  - Balanced compression (default)
    high    - Maximum compression, slower

═══════════════════════════════════════════════════════════════════════════════

COMPRESS_ADV - Advanced PDF compression with aggressive optimization
  Usage: python main.py compress_adv <pdf_file> [options]
  
  Options:
    --quality, -q INT     JPEG quality for rendered pages (1-100, default: 30)
    --max-width INT       Maximum width for pages (default: 1200)
    --max-height INT      Maximum height for pages (default: 1600)
    --output, -o FILE     Output PDF filename
  
  Examples:
    python main.py compress_adv large_file.pdf
    python main.py compress_adv large_file.pdf --quality 20 --max-width 1000
    python main.py compress_adv large_file.pdf -q 15 --max-width 800 --output tiny.pdf
  
  This method renders each page as a compressed image for maximum size reduction.
  Best for scanned documents and image-heavy PDFs where extreme compression is needed.

═══════════════════════════════════════════════════════════════════════════════

WORKFLOW EXAMPLES:

Complete PDF processing workflow:
  1. python main.py extract document.pdf
  2. python main.py rotate document_images --direction clockwise
  3. python main.py create_pdf document_images --output processed.pdf
  4. python main.py compress_adv processed.pdf --quality 70

PDF compression comparison:
  python main.py compress large.pdf --compression high
  python main.py compress_adv large.pdf --quality 60 --dpi 120

═══════════════════════════════════════════════════════════════════════════════

TIPS:
  • Use extract with quality filters to avoid tiny images
  • Rotate images before creating PDFs for proper orientation
  • Use basic compress for text-heavy PDFs
  • Use advanced compress for image-heavy PDFs
  • Lower quality/DPI values = smaller files but reduced image quality
  • Test different compression settings to find the best balance

For more information, visit: https://github.com/ifightcode/Python-PDF-Tools
"""
    print(help_text)

def main():
    parser = argparse.ArgumentParser(description="PDF Image Extractor, Image Rotator, and PDF Creator")
    parser.add_argument("command", choices=["extract", "rotate", "create_pdf", "compress", "compress_adv", "help"], help="Command to execute")
    parser.add_argument("path", nargs="?", help="Path to PDF file (for extract) or image directory (for rotate/create)")
    parser.add_argument("--direction", "-d", choices=["clockwise", "anticlockwise", "cw", "acw"], 
                       default="anticlockwise", help="Rotation direction (for rotate command)")
    parser.add_argument("--no-overwrite", action="store_true", 
                       help="Create new files instead of overwriting (for rotate command)")
    parser.add_argument("--output", "-o", type=str, 
                       help="Output PDF filename (for create_pdf/compress commands)")
    parser.add_argument("--compression", "-c", choices=["low", "medium", "high"], 
                       default="medium", help="Compression level (for compress command)")
    parser.add_argument("--quality", "-q", type=int, default=30,
                       help="JPEG quality for advanced compression (1-100, default: 30)")
    parser.add_argument("--max-width", type=int, default=1200,
                       help="Maximum width for rendered pages in advanced compression (default: 1200)")
    parser.add_argument("--max-height", type=int, default=1600,
                       help="Maximum height for rendered pages in advanced compression (default: 1600)")
    parser.add_argument("--min-width", type=int, default=50, 
                       help="Minimum image width for extraction (default: 50)")
    parser.add_argument("--min-height", type=int, default=50, 
                       help="Minimum image height for extraction (default: 50)")
    
    args = parser.parse_args()
    
    if args.command == "extract":
        # PDF extraction mode
        pdf_file = args.path
        
        if not os.path.exists(pdf_file):
            print(f"PDF file not found: {pdf_file}")
            return
        
        # Create output folder based on PDF name
        pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]
        output_dir = f"{pdf_name}_images"
        
        print(f"Extracting images from: {pdf_file}")
        print(f"Output folder: {output_dir}")
        
        # Extract images with quality filter
        extracted_count = extract_images_with_quality_filter(
            pdf_file, 
            output_dir, 
            min_width=args.min_width,
            min_height=args.min_height
        )
        
        print(f"\nExtraction complete! {extracted_count} images extracted.")
    
    elif args.command == "rotate":
        # Image rotation mode
        directory_path = args.path
        
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return
        
        # Rotate images
        rotated_count = rotate_images_in_directory(
            directory_path, 
            direction=args.direction,
            overwrite=not args.no_overwrite
        )
        
        print(f"\nRotation complete! {rotated_count} images rotated.")
    
    elif args.command == "create_pdf":
        # PDF creation mode
        directory_path = args.path
        
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return
        
        # Create PDF from images
        output_pdf = create_pdf_from_images(
            directory_path,
            output_pdf=args.output
        )
        
        if output_pdf:
            print(f"\nPDF creation complete! Created: {output_pdf}")
        else:
            print("\nPDF creation failed!")
    
    elif args.command == "compress":
        # PDF compression mode
        pdf_file = args.path
        
        if not os.path.exists(pdf_file):
            print(f"PDF file not found: {pdf_file}")
            return
        
        # Compress PDF
        compressed_pdf = compress_pdf(
            pdf_file,
            output_pdf=args.output,
            compression_level=args.compression
        )
        
        if compressed_pdf:
            print(f"\nPDF compression complete! Created: {compressed_pdf}")
        else:
            print("\nPDF compression failed!")
    
    elif args.command == "compress_adv":
        # Advanced PDF compression mode
        pdf_file = args.path
        
        if not os.path.exists(pdf_file):
            print(f"PDF file not found: {pdf_file}")
            return
        
        # Validate quality parameter
        if not 1 <= args.quality <= 100:
            print("Quality must be between 1 and 100")
            return
        
        # Validate dimensions
        if args.max_width < 200 or args.max_height < 200:
            print("Maximum width and height must be at least 200 pixels")
            return
        
        # Advanced compress PDF
        compressed_pdf = compress_pdf_advanced(
            pdf_file,
            output_pdf=args.output,
            image_quality=args.quality,
            max_width=args.max_width,
            max_height=args.max_height
        )
        
        if compressed_pdf:
            print(f"\nAdvanced PDF compression complete! Created: {compressed_pdf}")
        else:
            print("\nAdvanced PDF compression failed!")
    
    elif args.command == "help":
        # Show detailed help
        show_help()
        return

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, show help
        show_help()
    else:
        # Arguments provided, run command line mode
        main()