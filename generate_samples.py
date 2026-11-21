"""Generate realistic sample leaf images for instant 1-click UI demos."""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

SAMPLES_DIR = Path(r"c:\Users\Asus\OneDrive\Desktop\nndl project\PlantGuard-Crop-Disease-Detection\static\samples")
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

def create_leaf_base(bg_color=(240, 245, 240), leaf_color=(46, 125, 50)):
    img = Image.new("RGB", (224, 224), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw leaf shape (pointed oval / ellipse)
    draw.ellipse([45, 20, 179, 200], fill=leaf_color, outline=(27, 94, 32), width=2)
    # Add main center vein
    draw.line([112, 20, 112, 204], fill=(76, 175, 80), width=3)
    # Add secondary lateral veins
    for y in range(40, 180, 25):
        draw.line([112, y, 65, y + 20], fill=(76, 175, 80), width=1)
        draw.line([112, y, 159, y + 20], fill=(76, 175, 80), width=1)
    
    return img

def make_apple_scab():
    img = create_leaf_base(leaf_color=(56, 142, 60))
    draw = ImageDraw.Draw(img)
    # Olive/dark velvety scab spots
    scab_spots = [(90, 70, 25), (135, 110, 30), (80, 140, 22), (120, 155, 18)]
    for x, y, r in scab_spots:
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(44, 53, 30), outline=(20, 25, 15))
    img.save(SAMPLES_DIR / "sample_apple_scab.jpg", quality=92)
    print("Created sample_apple_scab.jpg")

def make_tomato_early_blight():
    img = create_leaf_base(leaf_color=(46, 125, 50))
    draw = ImageDraw.Draw(img)
    # Target-board concentric brown spots with chlorotic yellow halo
    blight_spots = [(100, 90, 32), (130, 145, 24)]
    for x, y, r in blight_spots:
        # Yellow chlorotic halo
        draw.ellipse([x - r - 8, y - r - 8, x + r + 8, y + r + 8], fill=(218, 165, 32))
        # Outer brown ring
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(101, 67, 33))
        # Inner darker center
        draw.ellipse([x - r // 2, y - r // 2, x + r // 2, y + r // 2], fill=(60, 35, 15))
    img.save(SAMPLES_DIR / "sample_tomato_early_blight.jpg", quality=92)
    print("Created sample_tomato_early_blight.jpg")

def make_corn_rust():
    img = Image.new("RGB", (224, 224), color=(240, 245, 240))
    draw = ImageDraw.Draw(img)
    # Elongated corn blade
    draw.rectangle([60, 0, 164, 224], fill=(67, 160, 71), outline=(46, 125, 50))
    # Parallel veins
    for x in range(70, 160, 12):
        draw.line([x, 0, x, 224], fill=(102, 187, 106), width=1)
    # Reddish-brown rust pustules
    np.random.seed(42)
    for _ in range(35):
        rx = np.random.randint(75, 150)
        ry = np.random.randint(20, 200)
        draw.ellipse([rx, ry, rx + 6, ry + 12], fill=(183, 65, 14), outline=(130, 40, 10))
    img.save(SAMPLES_DIR / "sample_corn_rust.jpg", quality=92)
    print("Created sample_corn_rust.jpg")

def make_healthy_pepper():
    img = create_leaf_base(leaf_color=(43, 140, 58))
    img.save(SAMPLES_DIR / "sample_healthy_pepper.jpg", quality=92)
    print("Created sample_healthy_pepper.jpg")

if __name__ == "__main__":
    make_apple_scab()
    make_tomato_early_blight()
    make_corn_rust()
    make_healthy_pepper()
    print("All demo samples generated successfully!")
