import os
import numpy as np
from PIL import Image
import cv2
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Flatten, Dense, Dropout
from tensorflow.keras.applications.vgg19 import VGG19

# ✅ Flask App Setup
app = Flask(__name__)
print('Models loaded. Visit http://127.0.0.1:5000/')

# ✅ Pneumonia Model
base_model_pneumonia = VGG19(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
x1 = base_model_pneumonia.output
x1 = Flatten()(x1)
x1 = Dense(128, activation='relu')(x1)
x1 = Dropout(0.2)(x1)
output1 = Dense(1, activation='sigmoid')(x1)
model_pneumonia = Model(inputs=base_model_pneumonia.input, outputs=output1)
model_pneumonia.load_weights('vgg_unfrozen.weights.h5')

# ✅ Brain Tumor Model (with 4 classes)
base_model_bt = VGG19(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
x2 = base_model_bt.output
x2 = Flatten()(x2)
x2 = Dense(128, activation='relu')(x2)
x2 = Dropout(0.2)(x2)
output2 = Dense(4, activation='softmax')(x2)  # ✅ 4 output classes
model_bt = Model(inputs=base_model_bt.input, outputs=output2)
model_bt.load_weights('brain_tumor_model.weights.h5')

# ✅ Image Preprocessing Function
def preprocess_image(img_path):
    image = cv2.imread(img_path)
    image = Image.fromarray(image).convert('RGB')
    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# ✅ Disease Prediction Logic
def predict_disease(img_path, disease_type):
    image = preprocess_image(img_path)

    if disease_type == "pneumonia":
        pred = model_pneumonia.predict(image)[0][0]
        return "Pneumonia" if pred > 0.5 else "Normal"

    elif disease_type == "brain":
        pred = model_bt.predict(image)[0]  # softmax output: [glioma, meningioma, no_tumor, pituitary]
        class_idx = np.argmax(pred)
        labels = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']  # ✅ match your folder order
        return labels[class_idx]

    else:
        return "Invalid Disease Type"

# ✅ Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        disease_type = request.form.get('disease')  # pneumonia or brain
        basepath = os.path.dirname(__file__)
        upload_folder = os.path.join(basepath, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, secure_filename(f.filename))
        f.save(file_path)

        result = predict_disease(file_path, disease_type)
        return result

    return None

if __name__ == '__main__':
    app.run(debug=True)
