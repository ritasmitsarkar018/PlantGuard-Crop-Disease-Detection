"""Smoke test for PlantGuard AI service, database, and inference pipeline."""
import io
import numpy as np
from PIL import Image
from model_service import service
import database

def main():
    print("1. Testing Database Initialization...")
    database.init_db()
    stats = database.get_scan_stats()
    print("Database OK! Current scans:", stats["total_scans"])

    print("\n2. Generating a test leaf image...")
    # Create a 224x224 RGB image with green background and brown spots
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    pixels = img.load()
    # Add brown spot simulating blight / lesion
    for x in range(80, 140):
        for y in range(80, 140):
            pixels[x, y] = (139, 69, 19)

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    print("\n3. Testing End-to-End Inference & Grad-CAM...")
    result = service.analyze_leaf(image_bytes, filename="test_leaf.jpg")
    print(f"Top Diagnosis: {result['crop']} - {result['disease']}")
    print(f"Confidence: {result['confidence_percentage']}")
    print(f"Severity: {result['severity']}")
    print(f"Grad-CAM Heatmap generated: {bool(result['gradcam']['heatmap'])}")
    print(f"Grad-CAM Overlay generated: {bool(result['gradcam']['overlay'])}")
    print(f"Top 5 classes count: {len(result['top_predictions'])}")

    print("\n4. Testing SQLite Scan Record...")
    scan_id = database.save_scan(
        filename="test_leaf.jpg",
        predicted_class=result["predicted_class"],
        crop=result["crop"],
        disease=result["disease"],
        confidence=result["confidence"],
        severity=result["severity"],
        top_predictions=result["top_predictions"],
        notes="Automated test scan"
    )
    print(f"Saved to scan_history with ID: {scan_id}")

    recent = database.get_recent_scans(5)
    print(f"Fetched {len(recent)} recent scans. Latest scan ID: {recent[0]['id']}")

    print("\nALL PIPELINE TESTS PASSED!")

if __name__ == "__main__":
    main()
