from django.shortcuts import render
import tensorflow as tf
import numpy as np
from django.http import JsonResponse
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array # type: ignore
from tensorflow.keras.applications.xception import preprocess_input  # type: ignore # Xception's preprocessing

from .models import DataModels

# Load the model globally when the server starts
database = DataModels.objects.last()

model = tf.keras.models.load_model(database.file.url)

def loadModelPrediction(request):
    if request.method == 'POST' and request.FILES.get('image_file'):
        # Get the uploaded image file
        image_file = request.FILES['image_file']

        try:
            # Open the image using Pillow
            img = Image.open(image_file)
            
            # Preprocess the image (resize and normalize)
            img = img.resize((224, 224))  # Resize to the input size of the model
            img = img_to_array(img)  # Convert to numpy array (from PIL image)
            
            # Apply Xception-specific preprocessing
            img = preprocess_input(img)  # Preprocess image as required by Xception

            # Add batch dimension
            img = np.expand_dims(img, axis=0)  # Shape should be (1, 224, 224, 3)
            
            # Make the prediction
            prediction = model.predict(img)
            
            # Convert the prediction to class label
            predicted_class = np.argmax(prediction, axis=1)[0]  # If model is classification
            confidence = np.max(prediction)  # Get the confidence score
            
            # Return the prediction as a JSON response
            return JsonResponse({
                'predicted_class': int(predicted_class),
                'confidence': float(confidence)
            })

        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)

    return JsonResponse({'error': 'No image file provided'}, status=400)
