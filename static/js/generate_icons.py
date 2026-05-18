"""
Generate Sonali Bank Icons
Run this script to generate all icon sizes
Requires: Pillow (pip install Pillow)
"""

from PIL import Image, ImageDraw
import os

def create_sonali_icon(size):
    """Create Sonali Bank icon with sun logo"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle (dark)
    margin = size // 10
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill='#1a1a2e'
    )
    
    # Middle circle (gold)
    margin2 = size // 4
    draw.ellipse(
        [margin2, margin2, size - margin2, size - margin2],
        fill='#c8960c'
    )
    
    # Inner circle (light gold)
    margin3 = size // 2.5
    draw.ellipse(
        [margin3, margin3, size - margin3, size - margin3],
        fill='#f0c430'
    )
    
    return img

def generate_all_icons():
    """Generate all required icon sizes"""
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    # Create icons directory if it doesn't exist
    os.makedirs('icons', exist_ok=True)
    
    for size in sizes:
        icon = create_sonali_icon(size)
        filename = f'icons/icon-{size}x{size}.png'
        icon.save(filename, 'PNG')
        print(f'Generated: {filename}')
    
    # Create favicon
    favicon = create_sonali_icon(32)
    favicon.save('icons/favicon.png', 'PNG')
    favicon.save('icons/favicon.ico', 'ICO')
    print('Generated: favicon.png and favicon.ico')

if __name__ == '__main__':
    generate_all_icons()
    print('\nAll icons generated successfully!')