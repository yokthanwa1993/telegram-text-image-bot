"""
Image generator module for creating text images with outline effect.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import io
import os

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()


def find_thai_font() -> str:
    """Find a suitable Thai bold font on the system."""
    font_paths = [
        # Project local font (preferred)
        SCRIPT_DIR / "fonts" / "PSLxOmyim-Bold.ttf",
        # macOS system fonts
        "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/07da2743cea0a1354e81aa4a33c736f3a8066a79.asset/AssetData/K2D.ttc",
        "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/cf0dc8d3b09f9ba379660e591e82566e2b557949.asset/AssetData/Sarabun.ttc",
        "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc",
        # Linux common paths
        "/usr/share/fonts/truetype/thai/Sarabun-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
    ]

    for path in font_paths:
        if Path(path).exists():
            return str(path)

    # Fallback to default
    return None


def draw_text_with_outline(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_color: str,
    outline_color: str = "#000000",
    outline_width: int = 8,
) -> None:
    """Draw text with outline effect."""
    x, y = position

    # Draw outline by drawing text multiple times around the position
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)

    # Draw main text
    draw.text(position, text, font=font, fill=fill_color)


def generate_text_image(
    line1: str,
    line2: str,
    font_size: int = 200,
    line1_color: str = "#F5A623",  # Orange/Yellow
    line2_color: str = "#FFFFFF",  # White
    outline_color: str = "#000000",  # Black
    outline_width: int = 16,
    padding: int = 20,
    line_spacing: int = 20,
    max_width: int = 1200,  # Maximum image width
    min_font_size: int = 60,  # Minimum font size
) -> bytes:
    """
    Generate a PNG image with two lines of text.

    Args:
        line1: First line of text (orange)
        line2: Second line of text (white)
        font_size: Font size in pixels
        line1_color: Color for first line
        line2_color: Color for second line
        outline_color: Color for text outline
        outline_width: Width of outline in pixels
        padding: Padding around the image
        line_spacing: Space between lines
        max_width: Maximum image width (auto-resize font if exceeded)
        min_font_size: Minimum font size when auto-resizing

    Returns:
        PNG image as bytes
    """
    font_path = find_thai_font()

    # Create a temporary image to measure text
    temp_img = Image.new('RGBA', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)

    # Auto-resize font if text is too wide
    current_font_size = font_size
    while current_font_size >= min_font_size:
        if font_path:
            font = ImageFont.truetype(font_path, current_font_size)
        else:
            font = ImageFont.load_default()
            break

        # Measure text width
        bbox1 = temp_draw.textbbox((0, 0), line1, font=font)
        bbox2 = temp_draw.textbbox((0, 0), line2, font=font)

        text1_width = bbox1[2] - bbox1[0]
        text2_width = bbox2[2] - bbox2[0]
        max_text_width = max(text1_width, text2_width)

        # Check if text fits within max_width (accounting for outline and padding)
        side_pad = outline_width * 2
        if max_text_width + side_pad * 2 <= max_width:
            break

        # Reduce font size and try again
        current_font_size -= 10

    # Recalculate with final font size
    # Adjust outline width proportionally if font was reduced
    if current_font_size < font_size:
        outline_width = max(8, int(outline_width * current_font_size / font_size))
        line_spacing = max(10, int(line_spacing * current_font_size / font_size))

    # Get text bounding boxes
    bbox1 = temp_draw.textbbox((0, 0), line1, font=font)
    bbox2 = temp_draw.textbbox((0, 0), line2, font=font)

    text1_width = bbox1[2] - bbox1[0]
    text1_height = bbox1[3] - bbox1[1]
    text2_width = bbox2[2] - bbox2[0]
    text2_height = bbox2[3] - bbox2[1]

    # Calculate image dimensions
    # Minimal top padding, extra bottom padding for Thai text descenders
    top_pad = outline_width + 5
    bottom_pad = outline_width * 4
    side_pad = outline_width * 2

    img_width = max(text1_width, text2_width) + side_pad * 2
    img_height = text1_height + text2_height + line_spacing + top_pad + bottom_pad

    # Create the actual image with transparent background
    img = Image.new('RGBA', (int(img_width), int(img_height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate positions (centered horizontally)
    x1 = (img_width - text1_width) // 2
    y1 = top_pad

    x2 = (img_width - text2_width) // 2
    y2 = y1 + text1_height + line_spacing

    # Draw text with outlines
    draw_text_with_outline(
        draw, (x1, y1), line1, font,
        fill_color=line1_color,
        outline_color=outline_color,
        outline_width=outline_width
    )

    draw_text_with_outline(
        draw, (x2, y2), line2, font,
        fill_color=line2_color,
        outline_color=outline_color,
        outline_width=outline_width
    )

    # Save to bytes
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)

    return output.getvalue()


if __name__ == "__main__":
    # Test the generator
    image_bytes = generate_text_image(
        "ฟองสบู่จัดเต็ม",
        "เหมือนอยู่ในฝัน!"
    )

    with open("test_output.png", "wb") as f:
        f.write(image_bytes)

    print("Test image saved to test_output.png")
