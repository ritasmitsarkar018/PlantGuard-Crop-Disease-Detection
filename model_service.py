import io
import json
import base64
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
import tensorflow as tf
import keras
from PIL import Image
import matplotlib
import matplotlib.cm as cm

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "best_crop_disease_model.keras"
CLASS_NAMES_PATH = BASE_DIR / "class_names.json"
KNOWLEDGE_PATH = BASE_DIR / "disease_knowledge.json"

IMAGE_SIZE = (224, 224)

class PlantGuardService:
    def __init__(self):
        self.model = None
        self.base_model = None
        self.grad_model = None
        self.class_names = []
        self.knowledge = {}
        self.crop_to_indices = {}
        self._load_resources()

    def _load_resources(self):
        print(f"Loading class labels from {CLASS_NAMES_PATH}...")
        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
            self.class_names = json.load(f)

        # Index classes by crop family
        for idx, c_name in enumerate(self.class_names):
            crop_prefix = c_name.split("___")[0].replace("_", " ").strip()
            # Clean crop names like "Pepper, bell" -> "Pepper" or "Bell Pepper"
            if "Pepper" in crop_prefix:
                clean_crop = "Pepper"
            elif "Corn" in crop_prefix:
                clean_crop = "Corn"
            else:
                clean_crop = crop_prefix.split()[0]
                
            self.crop_to_indices.setdefault(clean_crop.lower(), []).append(idx)
            self.crop_to_indices.setdefault(crop_prefix.lower(), []).append(idx)

        print(f"Loading disease knowledge base from {KNOWLEDGE_PATH}...")
        if KNOWLEDGE_PATH.exists():
            with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                self.knowledge = json.load(f)
        else:
            self.knowledge = {}

        print(f"Loading trained model from {MODEL_PATH}...")
        self.model = keras.models.load_model(str(MODEL_PATH))
        
        # Prepare Grad-CAM intermediate model
        try:
            self.base_model = self.model.get_layer("mobilenetv2_1.00_224")
            last_conv_layer = self.base_model.get_layer("out_relu")
            self.grad_model = keras.Model(
                inputs=self.base_model.inputs,
                outputs=[last_conv_layer.output, self.base_model.output]
            )
            print("Grad-CAM explainability pipeline initialized successfully!")
        except Exception as e:
            print(f"Warning: Could not initialize Grad-CAM model: {e}")
            self.grad_model = None

    def preprocess_image(self, pil_img: Image.Image) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocesses image to (1, 224, 224, 3) preserving aspect ratio using letterboxing."""
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        
        w, h = pil_img.size
        # Aspect-ratio preserving letterbox
        scale = min(IMAGE_SIZE[0] / w, IMAGE_SIZE[1] / h)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        resized_img = pil_img.resize((nw, nh), Image.Resampling.LANCZOS)
        
        # Center on black canvas
        boxed_img = Image.new("RGB", IMAGE_SIZE, (0, 0, 0))
        boxed_img.paste(resized_img, ((IMAGE_SIZE[0] - nw) // 2, (IMAGE_SIZE[1] - nh) // 2))
        
        img_array = np.array(boxed_img, dtype=np.float32)
        display_img = np.copy(img_array)
        
        # MobileNetV2 scaling (-1 to 1)
        preprocessed = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        batch_input = np.expand_dims(preprocessed, axis=0)
        
        return batch_input, display_img

    def compute_gradcam(
        self, 
        batch_input: np.ndarray, 
        target_class_idx: int,
        display_img: np.ndarray
    ) -> Tuple[str, str, str]:
        """Generates Grad-CAM heatmap and overlay for the specified class index."""
        if self.grad_model is None:
            return "", "", ""

        with tf.GradientTape() as tape:
            conv_outputs, base_output = self.grad_model(batch_input)
            tape.watch(conv_outputs)
            
            x = self.model.get_layer("global_average_pooling2d")(base_output)
            x = self.model.get_layer("dropout")(x, training=False)
            preds = self.model.get_layer("disease_probabilities")(x)
            loss = preds[:, target_class_idx]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        conv_outputs_val = conv_outputs[0]
        cam = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs_val), axis=-1).numpy()
        
        cam = np.maximum(cam, 0)
        max_val = np.max(cam)
        if max_val > 0:
            cam = cam / max_val
        else:
            cam = np.zeros_like(cam)

        cam_img = Image.fromarray(np.uint8(cam * 255)).resize(IMAGE_SIZE, Image.Resampling.BICUBIC)
        cam_array = np.array(cam_img, dtype=np.float32) / 255.0

        colormap = matplotlib.colormaps["jet"]
        colored_cam = colormap(cam_array)
        colored_cam_rgb = (colored_cam[:, :, :3] * 255).astype(np.uint8)

        alpha = 0.45
        overlay = (display_img * (1 - alpha) + colored_cam_rgb * alpha).astype(np.uint8)

        def to_base64(img_arr: np.ndarray) -> str:
            pil = Image.fromarray(img_arr.astype(np.uint8))
            buffered = io.BytesIO()
            pil.save(buffered, format="JPEG", quality=90)
            encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded}"

        orig_b64 = to_base64(display_img)
        heat_b64 = to_base64(colored_cam_rgb)
        over_b64 = to_base64(overlay)

        return orig_b64, heat_b64, over_b64

    def analyze_leaf(
        self, 
        image_bytes: bytes, 
        filename: str = "upload.jpg", 
        crop_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs deep learning inference with optional crop-level constraint.
        If crop_filter is provided (e.g. 'Apple', 'Tomato'), predictions are constrained
        and re-normalized within that crop's diseases.
        """
        pil_img = Image.open(io.BytesIO(image_bytes))
        batch_input, display_img = self.preprocess_image(pil_img)

        # Raw model predictions across all 38 classes
        raw_predictions = self.model.predict(batch_input, verbose=0)[0]
        
        # Check if user specified a crop filter
        active_indices = list(range(len(self.class_names)))
        is_filtered = False
        
        if crop_filter and crop_filter.lower() != "auto":
            clean_filter = crop_filter.lower().strip()
            # Match against registered crop families
            matching_indices = self.crop_to_indices.get(clean_filter, [])
            if not matching_indices:
                # Substring match fallback
                matching_indices = [
                    i for i, c in enumerate(self.class_names) 
                    if clean_filter in c.lower()
                ]
            if matching_indices:
                active_indices = list(set(matching_indices))
                is_filtered = True

        # Compute probabilities over active indices
        if is_filtered:
            subset_raw = np.array([raw_predictions[i] for i in active_indices])
            subset_sum = np.sum(subset_raw)
            if subset_sum > 0:
                normalized_probs = subset_raw / subset_sum
            else:
                normalized_probs = np.ones_like(subset_raw) / len(subset_raw)
            
            # Sort within crop
            sort_order = np.argsort(normalized_probs)[::-1]
            top_active_indices = [active_indices[k] for k in sort_order]
            top_active_probs = [float(normalized_probs[k]) for k in sort_order]
        else:
            sort_order = np.argsort(raw_predictions)[::-1]
            top_active_indices = [int(i) for i in sort_order[:5]]
            top_active_probs = [float(raw_predictions[i]) for i in top_active_indices]

        # Build top predictions list
        top_predictions = []
        for i, idx in enumerate(top_active_indices[:5]):
            c_name = self.class_names[idx]
            info = self.knowledge.get(c_name, {})
            prob = top_active_probs[i]
            top_predictions.append({
                "class_name": c_name,
                "crop": info.get("crop", c_name.split("___")[0].replace("_", " ")),
                "disease": info.get("disease", c_name.split("___")[-1].replace("_", " ")),
                "probability": round(prob, 4),
                "percentage": f"{prob * 100:.1f}%",
                "is_healthy": info.get("is_healthy", "healthy" in c_name.lower())
            })

        # Primary prediction
        best_idx = top_active_indices[0]
        best_class = self.class_names[best_idx]
        best_prob = top_active_probs[0]
        best_info = self.knowledge.get(best_class, {})

        # Compute Grad-CAM for best class
        orig_b64, heat_b64, over_b64 = self.compute_gradcam(batch_input, best_idx, display_img)

        # Detect candidate crops for easy 1-click UI switching
        crop_scores = {}
        for idx, p in enumerate(raw_predictions):
            c_name = self.class_names[idx]
            c_crop = c_name.split("___")[0].replace("_", " ")
            crop_scores[c_crop] = crop_scores.get(c_crop, 0.0) + float(p)
        
        suggested_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
        top_crop_names = [c[0] for c in suggested_crops[:4] if c[1] > 0.0001]

        return {
            "predicted_class": best_class,
            "crop": best_info.get("crop", best_class.split("___")[0].replace("_", " ")),
            "disease": best_info.get("disease", best_class.split("___")[-1].replace("_", " ")),
            "confidence": round(best_prob, 4),
            "confidence_percentage": f"{best_prob * 100:.1f}%",
            "is_healthy": best_info.get("is_healthy", "healthy" in best_class.lower()),
            "severity": best_info.get("severity", "Medium" if "healthy" not in best_class.lower() else "None"),
            "symptoms": best_info.get("symptoms", "No symptom data available."),
            "organic_treatment": best_info.get("organic_treatment", "Apply standard organic plant care practices."),
            "chemical_treatment": best_info.get("chemical_treatment", "Consult local extension services for approved fungicides."),
            "prevention": best_info.get("prevention", "Maintain balanced soil fertility and proper irrigation."),
            "is_crop_filtered": is_filtered,
            "applied_filter": crop_filter if is_filtered else "auto",
            "candidate_crops": top_crop_names,
            "top_predictions": top_predictions,
            "gradcam": {
                "original": orig_b64,
                "heatmap": heat_b64,
                "overlay": over_b64
            }
        }

# Global singleton
service = PlantGuardService()
