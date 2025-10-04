# ==========================================
# Assignment 9 - Amazon SageMaker Experiment
# ==========================================
# Use Amazon SageMaker to deploy a pre-trained image classification model,
# send a test image, and print the model prediction.

# ---------------------------
# STEP 0: Install Dependencies
# ---------------------------
!pip install --upgrade sagemaker
!pip install requests

import sagemaker
import boto3
import json
import base64
from sagemaker.jumpstart.model import JumpStartModel
from PIL import Image
import requests
from io import BytesIO
import time


# ---------------------------
# STEP 1: Setup SageMaker Session & Role
# ---------------------------
print("Step 1: Setting up SageMaker session and IAM role...")

sagemaker_session = sagemaker.Session()
aws_region = sagemaker_session.boto_region_name
role = sagemaker.get_execution_role()

print(f"SageMaker session established in region: {aws_region}")
print(f"Using IAM role: {role}")


# ---------------------------
# STEP 2: Deploy Pre-trained Model from JumpStart
# ---------------------------
print("\nStep 2: Deploying pre-trained model...")

# Use TensorFlow MobileNetV2 pre-trained image classification model
model_id = "tensorflow-ic-mobilenet-v2-100-224-classification"
endpoint_name = f'jumpstart-{model_id}-endpoint'

# Create JumpStart model
model = JumpStartModel(model_id=model_id)

# Deploy to SageMaker endpoint
predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.xlarge',   # adjust based on quota/cost
    endpoint_name=endpoint_name,
    wait=True
)

print(f"Endpoint '{predictor.endpoint_name}' deployed successfully.")


# ---------------------------
# STEP 3: Download & Preprocess Test Image
# ---------------------------
print("\nStep 3: Preparing test image for inference...")

image_url = "https://hips.hearstapps.com/hmg-prod/images/dog-puppy-on-garden-royalty-free-image-1586968018.jpg"

try:
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    print("Test image downloaded successfully.")
except Exception as e:
    raise RuntimeError(f"Error downloading image: {e}")

# Resize image to model's expected input (224x224)
resized_image = image.resize((224, 224))
image_bytes = BytesIO()
resized_image.save(image_bytes, format="JPEG")
image_bytes = image_bytes.getvalue()

# Convert to Base64 encoding
image_b64 = base64.b64encode(image_bytes).decode("utf-8")
payload = {"instances": [{"b64": image_b64}]}


# ---------------------------
# STEP 4: Invoke Endpoint & Get Prediction
# ---------------------------
print("\nStep 4: Invoking the endpoint with the test image...")

try:
    prediction = predictor.predict(payload)

    if prediction and "predictions" in prediction:
        top_prediction = prediction["predictions"]

        print("\nPrediction received:")
        print(json.dumps(top_prediction, indent=2))

        # Extract top predicted class index & confidence
        predicted_index = max(top_prediction, key=top_prediction.get)
        confidence = top_prediction[predicted_index]

        print(f"\nTop Predicted Class Index: {predicted_index}")
        print(f"Confidence: {confidence:.4f}")
    else:
        print("Error: Invalid prediction response format.")
        print(f"Full response: {prediction}")

except Exception as e:
    print(f"Error invoking endpoint: {e}")


# ---------------------------
# STEP 5: Clean Up Resources
# ---------------------------
print("\nStep 5: Cleaning up SageMaker endpoint...")

try:
    predictor.delete_endpoint()
    print(f"Endpoint '{predictor.endpoint_name}' deleted successfully.")
except Exception as e:
    print(f"An error occurred while deleting the endpoint: {e}")
