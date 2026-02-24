from PIL import Image, ImageDraw
import io

def create_app_icon():
    """Create app icon from SVG concept using PIL"""
    # Create a 256x256 image with transparent background
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle with gradient effect
    center = 128
    radius = 120
    
    # Create gradient background
    for r in range(radius, 0, -2):
        # Blue gradient from light to dark
        intensity = int(255 * (radius - r) / radius)
        color = (59 + intensity//3, 130 + intensity//4, 246, 220)
        draw.ellipse([center-r, center-r, center+r, center+r], fill=color)
    
    # Main storage boxes (stacked)
    # Bottom box
    draw.rounded_rectangle([65, 75, 125, 120], radius=4, fill=(255, 255, 255, 230))
    draw.rounded_rectangle([67, 77, 123, 118], radius=2, outline=(30, 64, 175), width=2)
    
    # Middle box
    draw.rounded_rectangle([80, 65, 125, 100], radius=3, fill=(255, 255, 255, 200))
    draw.rounded_rectangle([82, 67, 123, 98], radius=2, outline=(30, 64, 175), width=2)
    
    # Top box
    draw.rounded_rectangle([95, 55, 130, 83], radius=3, fill=(255, 255, 255, 180))
    draw.rounded_rectangle([97, 57, 128, 81], radius=2, outline=(30, 64, 175), width=2)
    
    # Chart area
    chart_x, chart_y = 140, 90
    draw.rounded_rectangle([chart_x, chart_y, chart_x+80, chart_y+60], radius=6, 
                          fill=(255, 255, 255, 230))
    
    # Chart bars (sales growth)
    bar_colors = (16, 185, 129)  # Green color
    bars = [(10, 35, 15), (22, 28, 22), (34, 20, 30), (46, 25, 25), (58, 15, 35)]
    
    for x, y, height in bars:
        draw.rectangle([chart_x + x, chart_y + y, chart_x + x + 8, chart_y + y + height], 
                      fill=bar_colors)
    
    # Grid lines
    for y in [20, 30, 40, 50]:
        draw.line([chart_x + 8, chart_y + y, chart_x + 70, chart_y + y], 
                 fill=(229, 231, 235), width=1)
    
    # Dollar sign circle (sales)
    draw.ellipse([65, 155, 115, 205], fill=(16, 185, 129, 230))
    # Simple dollar sign representation
    draw.text((90, 175), "$", fill=(255, 255, 255), anchor="mm")
    
    # Package icon circle (inventory)
    draw.ellipse([145, 155, 195, 205], fill=(245, 158, 11, 230))
    # Simple package representation
    draw.rectangle([158, 168, 182, 186], outline=(255, 255, 255), width=2)
    draw.line([158, 177, 182, 177], fill=(255, 255, 255), width=2)
    draw.line([167, 168, 167, 186], fill=(255, 255, 255), width=2)
    
    # Save the image
    img.save('assets/icons/app_icon.png', 'PNG')
    
    # Create different sizes for Windows
    sizes = [16, 24, 32, 48, 64, 128, 256]
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'assets/icons/icon_{size}.png', 'PNG')
    
    print("App icons created successfully!")

if __name__ == "__main__":
    create_app_icon()
