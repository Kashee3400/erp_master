import fitz  # PyMuPDF
from PIL import Image

def add_background_watermark(input_pdf_path, watermark_image_path, output_pdf_path, opacity=0.25):
    # Open the PDF
    pdf_document = fitz.open(input_pdf_path)

    # Load and apply opacity to the image
    with Image.open(watermark_image_path).convert("RGBA") as img:
        alpha = img.split()[3] if img.mode == 'RGBA' else Image.new('L', img.size, 255)
        alpha = alpha.point(lambda p: int(p * opacity))
        img.putalpha(alpha)
        temp_image_path = "temp_watermark.png"
        img.save(temp_image_path)

    # Iterate through each page
    for page in pdf_document:
        page_width, page_height = page.rect.width, page.rect.height
        img_width, img_height = img.size
        img_aspect_ratio = img_width / img_height
        page_aspect_ratio = page_width / page_height

        # Determine dimensions
        if img_aspect_ratio > page_aspect_ratio:
            new_width = page_width
            new_height = new_width / img_aspect_ratio
        else:
            new_height = page_height
            new_width = new_height * img_aspect_ratio

        # Center the image
        x0 = (page_width - new_width) / 2
        y0 = (page_height - new_height) / 2
        x1 = x0 + new_width
        y1 = y0 + new_height

        # Insert image (no opacity arg here)
        page.insert_image(
            fitz.Rect(x0, y0, x1, y1),
            filename=temp_image_path,
            overlay=False,
            keep_proportion=True
        )

    # Save output
    pdf_document.save(output_pdf_path)
    pdf_document.close()

# Example usage
add_background_watermark(
    "C:/Users/Kashee/Downloads/chunar_incentive.pdf",
    "C:/Users/Kashee/Downloads/background.jpg",
    "K:/incentives/chunar_incentive.pdf",
    opacity=1
)
