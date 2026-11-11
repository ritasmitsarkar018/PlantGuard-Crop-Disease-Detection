# 🌱 PlantGuard – AI-Based Crop Disease Detection

**An AI-powered crop disease detection system using Deep Learning and TensorFlow.**

PlantGuard is an image-based crop disease classification project that uses a trained deep learning model to identify plant diseases from leaf photographs. The system predicts the most likely disease class and provides confidence scores for its predictions.

---

## 📌 Project Overview

Agricultural crop diseases can significantly affect crop quality and productivity. Early identification can help farmers take appropriate preventive measures.

PlantGuard aims to simplify preliminary disease identification by allowing users to upload a photograph of a crop leaf and receive AI-generated predictions.

The project uses the PlantVillage dataset and MobileNetV2-based deep learning techniques.

## 🎯 Objectives

- Detect crop diseases from leaf images.
- Classify images into 38 PlantVillage classes.
- Use transfer learning to improve image classification.
- Display the top predicted classes with confidence scores.
- Evaluate model performance using standard classification metrics.
- Provide an accessible demonstration interface.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Programming language |
| TensorFlow / Keras | Deep learning framework |
| MobileNetV2 | Transfer learning architecture |
| NumPy | Numerical computations |
| Pandas | Data handling |
| Matplotlib | Visualization |
| Scikit-learn | Model evaluation |
| Gradio | Interactive demonstration interface |
| Google Colab | Model training and experimentation |

## 📂 Dataset

**PlantVillage Dataset**

The project uses the PlantVillage dataset, containing images of healthy and diseased plant leaves.

- 38 classification categories.
- Images covering multiple crop types.
- Healthy and diseased leaf samples.

## 🧠 Model Architecture

PlantGuard uses MobileNetV2 as its deep learning architecture.

**Model input dimensions:** 224 × 224 × 3

The prediction pipeline consists of:

1. Upload a leaf photograph.
2. Convert the image into RGB format.
3. Resize the image to 224 × 224 pixels.
4. Apply MobileNetV2 preprocessing.
5. Pass the image through the trained model.
6. Generate class probabilities.
7. Display the top 5 predictions.

## 📊 Model Evaluation

The project includes the following evaluation resources:

- Training and validation curves.
- Confusion matrix.
- Classification report.
- Evaluation metrics in JSON format.

These resources are included in the repository for performance analysis.

## 🚀 Project Files

| File | Description |
|---|---|
| `Crop_Disease_Detection_TensorFlow_Starter (1).ipynb` | Complete Google Colab notebook |
| `best_crop_disease_model.keras` | Best saved trained model |
| `crop_disease_model.keras` | Trained model |
| `class_names.json` | Classification labels |
| `evaluation_metrics.json` | Evaluation metrics |
| `classification_report.txt` | Classification report |
| `confusion_matrix.png` | Confusion matrix visualization |
| `training_curves.png` | Training performance visualization |

## 💻 How to Run the Project

### Option 1: Google Colab

1. Download or clone this repository.
2. Open the `.ipynb` notebook in Google Colab.
3. Upload the trained model and supporting JSON file if required.
4. Run the model-loading and prediction cells.
5. Upload a crop-leaf photograph.
6. View the top 5 predicted classes and confidence scores.

### Option 2: Local Environment

Install the required dependencies:

```bash
pip install tensorflow numpy pillow matplotlib scikit-learn gradio
```

Load the trained model:

```python
import tensorflow as tf
import json

model = tf.keras.models.load_model(
    "best_crop_disease_model.keras"
)

with open("class_names.json", "r") as f:
    CLASS_NAMES = json.load(f)
```

Use the notebook for the complete prediction implementation.

## ⚠️ Disclaimer

PlantGuard is an educational and experimental AI prototype. Its predictions should be treated as preliminary screening assistance and not as a guaranteed agricultural diagnosis.

Consult an agricultural expert before taking crop treatment decisions.

## 🔮 Future Scope

- Expand the dataset with more crop varieties.
- Improve model accuracy and generalization.
- Develop a mobile-friendly application.
- Integrate multilingual support.
- Provide disease management recommendations.
- Deploy the model through a cloud-based API.

## 👥 Contributors

**Project Team – PlantGuard**

- RITASMIT SARKAR – Project Lead

Additional team members can be added here.

---

**PlantGuard – Empowering Agriculture Through Artificial Intelligence 🌱**
