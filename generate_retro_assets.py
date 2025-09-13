# Generates CRT scanline overlay and red pixel overlay PNGs for retro UI
from PIL import Image, ImageDraw

def generate_crt_scanlines(path, width=1600, height=1100, line_spacing=3, alpha=60):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    for y in range(0, height, line_spacing):
        draw.line([(0, y), (width, y)], fill=(0,0,0,alpha), width=1)
    img.save(path)

def generate_red_pixel_overlay(path, size=32, alpha=120):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,size-1,size-1], fill=(255,0,0,alpha))
    img.save(path)

if __name__ == "__main__":
    generate_crt_scanlines("Hackathon_image/crt_scanlines.png")
    generate_red_pixel_overlay("Hackathon_image/red_overlay.png")
    print("Retro assets generated: crt_scanlines.png, red_overlay.png")
