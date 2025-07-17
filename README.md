# PDF Tools

A comprehensive Python utility for PDF processing, image manipulation, and **extreme PDF compression** (99%+ file size reduction).

## Features

- **PDF Image Extraction**: Extract all images from PDF files with quality filtering
- **Image Rotation**: Rotate images clockwise or anticlockwise by 90 degrees
- **PDF Creation**: Create PDFs from images following page numbering convention
- **PDF Compression**: Extreme compression with 99%+ file size reduction using page rendering
- **Interactive Help System**: Comprehensive built-in documentation and examples
- **Batch Processing**: Process all images in a directory at once
- **Multiple Formats**: Supports PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP
- **Flexible Options**: Overwrite originals or create new files

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. If you don't have uv installed, install it first:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install the project dependencies:

```bash
uv sync
```

## Usage

### Command Line Interface

The tool supports five main commands: `extract`, `rotate`, `create_pdf`, `compress`, and `help`.

#### Extract Images from PDF

Extract all images from a PDF file:

```bash
uv run main.py extract path/to/your/file.pdf
```

**Options:**
- `--min-width`: Minimum image width for extraction (default: 50)
- `--min-height`: Minimum image height for extraction (default: 50)

**Example:**
```bash
uv run main.py extract deed.pdf --min-width 100 --min-height 100
```

This will create a folder named `{pdf_name}_images` containing all extracted images.

#### Rotate Images

Rotate all images in a directory:

```bash
# Rotate anticlockwise (default)
uv run main.py rotate path/to/image/directory

# Rotate clockwise
uv run main.py rotate path/to/image/directory --direction clockwise
```

**Direction Options:**
- `anticlockwise` or `acw` - Rotate 90° counterclockwise (default)
- `clockwise` or `cw` - Rotate 90° clockwise

**Additional Options:**
- `--no-overwrite` - Create new files instead of overwriting originals
- `--direction` or `-d` - Specify rotation direction

**Examples:**
```bash
# Rotate images anticlockwise (overwrites originals)
uv run main.py rotate deed_images

# Rotate images clockwise
uv run main.py rotate deed_images --direction clockwise
uv run main.py rotate deed_images -d cw

# Rotate clockwise and keep originals
uv run main.py rotate deed_images -d clockwise --no-overwrite

# Rotate anticlockwise with short form
uv run main.py rotate deed_images -d acw
```

#### Create PDF from Images

Create a PDF from images in a directory that follow the page numbering convention:

```bash
# Create PDF with auto-generated name
uv run main.py create_pdf path/to/image/directory

# Create PDF with custom name
uv run main.py create_pdf path/to/image/directory --output custom_name.pdf
```

**Naming Convention:**
The tool looks for images with the pattern `*_page{N}_*.ext` where `{N}` is the page number:
- `deed_page1_img1.png`
- `deed_page2_img1.png`
- `contract_page10_scan.jpg`

**Options:**
- `--output` or `-o` - Specify custom output PDF filename

**Examples:**
```bash
# Create PDF from deed_images folder (creates deed_images_combined.pdf)
uv run main.py create_pdf deed_images

# Create PDF with custom name
uv run main.py create_pdf deed_images --output my_document.pdf
uv run main.py create_pdf deed_images -o final_deed.pdf
```

#### Compress PDF

**🚀 EXTREME COMPRESSION** - Achieve 99%+ file size reduction! This method renders each PDF page as a compressed image for maximum size reduction:

```bash
# Compression with default settings (99%+ reduction typical)
uv run main.py compress path/to/your/file.pdf

# Custom quality and resolution settings
uv run main.py compress path/to/your/file.pdf --quality 20 --max-width 1000

# Ultra compression for maximum size reduction
uv run main.py compress path/to/your/file.pdf --quality 10 --max-width 800 --output tiny_file.pdf
```

**Options:**
- `--quality` or `-q` - JPEG quality for rendered pages (1-100, default: 30)
- `--max-width` - Maximum page width in pixels (default: 1200)
- `--max-height` - Maximum page height in pixels (default: 1600)
- `--output` or `-o` - Specify custom output PDF filename

**Real-World Results:**
```
📊 Compression Test Results:
Original PDF:      162.81 MB
Compressed PDF:      0.59 MB  (99.6% reduction - 275x smaller!)
Ultra compressed:    0.26 MB  (99.8% reduction - 626x smaller!)
```

**Examples:**
```bash
# Default compression (creates original_advanced_compressed.pdf)
uv run main.py compress large_document.pdf

# Balanced compression (good quality, excellent size reduction)
uv run main.py compress large_document.pdf --quality 30 --max-width 1200

# High compression (very good size reduction, acceptable quality)
uv run main.py compress large_document.pdf --quality 20 --max-width 1000

# Ultra compression (maximum size reduction, basic quality)
uv run main.py compress large_document.pdf -q 10 --max-width 800 -o ultra_tiny.pdf
```

**Perfect For:**
- 📄 Scanned documents and image-heavy PDFs
- 📧 Email attachments with size limits
- 💾 Archival storage where space matters
- 🌐 Web distribution requiring small file sizes
- 📱 Mobile viewing and sharing

**Quality Guidelines:**
- **Quality 30** (default): Excellent balance - 99%+ reduction, good readability
- **Quality 20**: High compression - 99%+ reduction, very readable
- **Quality 10**: Maximum compression - 99.8%+ reduction, basic readability

#### Get Help

Access comprehensive documentation and examples:

```bash
uv run main.py help
```

This displays detailed usage information for all commands, including examples and tips.

### Getting Started

If you run the script without arguments, it displays comprehensive help documentation:

```bash
uv run main.py
```

This shows all available commands, options, examples, and usage tips.

## Examples

### Complete Workflow

1. **Extract images from a PDF:**
   ```bash
   uv run main.py extract document.pdf
   ```
   This creates a `document_images/` folder with extracted images.

2. **Rotate the extracted images:**
   ```bash
   uv run main.py rotate document_images --direction clockwise
   ```

3. **Create a new PDF from the rotated images:**
   ```bash
   uv run main.py create_pdf document_images --output rotated_document.pdf
   ```

4. **Compress the final PDF (optional):**
   ```bash
   uv run main.py compress rotated_document.pdf --quality 20 --output final_compressed.pdf
   ```

### Batch Processing

Process multiple operations:

```bash
# Extract from PDF
uv run main.py extract contract.pdf --min-width 200

# Rotate extracted images without overwriting
uv run main.py rotate contract_images --direction anticlockwise --no-overwrite

# Create PDF from processed images
uv run main.py create_pdf contract_images --output final_contract.pdf
```

## Supported Image Formats

The rotation function supports these image formats:
- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF
- WEBP

## Output

### PDF Extraction
- Creates a directory named `{pdf_name}_images`
- Images are named as `{pdf_name}_page{N}_img{M}.png`
- Shows progress and image dimensions during extraction

### Image Rotation
- **With overwrite (default)**: Modifies original files
- **Without overwrite**: Creates new files with `_rotated_{direction}` suffix
- Shows progress for each rotated image

## Dependencies

- **PyMuPDF**: For PDF processing and image extraction
- **Pillow (PIL)**: For image manipulation and rotation

## Error Handling

The tool includes robust error handling:
- Validates file and directory paths
- Handles unsupported image formats gracefully
- Reports errors for individual files while continuing batch processing
- Provides clear error messages and usage instructions

## Development

To contribute or modify the code:

1. Clone the repository
2. Install dependencies: `uv sync`
3. Make your changes
4. Test with sample files

## License

This project is open source. Feel free to use and modify as needed.