from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import tensorflow as tf
import numpy as np
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array  # type: ignore
from tensorflow.keras.applications.xception import preprocess_input  # type: ignore # Xception's preprocessing

from .models import DataModels

from django.shortcuts import render


def index(request):
    return render(request, 'index.html',{})

hama_data = {
    0: {
        "nama_hama": "Hama Perusak Daun (Plutella Xylostella)",
        "penanganan": [
            "Gunakan insektisida berbahan aktif abamektin, klorantraniliprol, atau spinosad.",
            "Semprotkan secara selektif untuk mencegah resistensi."
        ]
    },
    1: {
        "nama_hama": "Ulat Tanah (Agrotis sp.)",
        "penanganan": [
            "Gunakan insektisida berbahan aktif klorpirifos atau karbofuran di sekitar area pangkal tanaman.",
            "Bersihkan gulma dan sisa tanaman yang dapat menjadi tempat berkembangnya hama."
        ]
    },
    2: {
        "nama_hama": "Ulat Grayak (Spodoptera litura)",
        "penanganan": [
            "Gunakan insektisida berbahan aktif emamektin benzoat, deltametrin, atau lambda-sihalotrin.",
            "Pastikan tanaman mendapatkan nutrisi yang cukup agar lebih tahan terhadap serangan hama."
        ]
    },
    3: {
        "nama_hama": "Hama Kutu Putih (Phenacoccus manihoti)",
        "penanganan": [
            "Gunakan insektisida berbahan aktif imidakloprid, asetamiprid, atau dimetoat.",
            "Semprotkan insektisida secara merata di bagian tanaman yang terinfestasi."
        ]
    }
}

def tampilkan_penanganan(id_deteksi):
    if id_deteksi in hama_data:
        hama = hama_data[id_deteksi]
        return hama["penanganan"]
    else:
        return {"error": "ID deteksi tidak ditemukan. Pastikan ID valid (0, 1, 2, dst.)."}

class LoadModelPredictionView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        print(request)
        if 'image' not in request.FILES:
            return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']

        try:
            # Fetch the latest model from the database
            database = DataModels.objects.last()
            if not database or not database.file:
                return Response({'error': 'No model found in the database'}, status=status.HTTP_404_NOT_FOUND)

            model = tf.keras.models.load_model(database.file.path)  # Load the model file

            # Process the uploaded image
            img = Image.open(image_file)
            if img.mode != 'RGB':
                img = img.convert('RGB') 

            img = img.resize((224, 224))
            img = img_to_array(img)
            img = preprocess_input(img)
            img = np.expand_dims(img, axis=0)

            # Make predictions
            prediction = model.predict(img)
            print(prediction)
            predicted_class = np.argmax(prediction, axis=1)[0]  # Class index
            print(np.argmax(prediction, axis=1))
            class_indices = {0: 'Agrotis Sp', 1: 'Phenacoccus Manihoti', 2: 'Plutella Xylostella', 3: 'Spodoptera Litura'}  # Modify with your actual class indices
            predicted_class_name = class_indices[predicted_class] 
            confidence = np.max(prediction)  # Confidence score

            penanganan =  tampilkan_penanganan(predicted_class)

            return Response({
                'predicted_class': int(predicted_class),
                'class_name': str(predicted_class_name),
                'confidence': float(confidence),
                'penanganan': penanganan
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
