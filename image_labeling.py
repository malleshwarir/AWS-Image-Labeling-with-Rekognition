import boto3
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO

def detect_labels(photo, bucket):
    client = boto3.client('rekognition', region_name='ap-south-1')
    s3 = boto3.client('s3', region_name='ap-south-1')

    try:
        
        response = client.detect_labels(Image={'S3Object': {'Bucket': "imagelabels-bucket", 'Name': photo}}, MaxLabels=10, MinConfidence=80)

        print(f"\nDetected labels for '{photo}':")
        for label in response['Labels']:
            print(f"{label['Name']} ({label['Confidence']:.2f}%)")
        
        img_data = s3.get_object(Bucket=bucket, Key=photo)['Body'].read()
        img = Image.open(BytesIO(img_data))

        plt.imshow(img)
        ax = plt.gca()

        for label in response['Labels']:
            for instance in label.get('Instances', []): 
                if 'BoundingBox' in instance:
                    bbox = instance['BoundingBox']
                    left, top = bbox['Left'] * img.width, bbox['Top'] * img.height
                    width, height = bbox['Width'] * img.width, bbox['Height'] * img.height

                    rect = patches.Rectangle((left, top), width, height, linewidth=2, edgecolor='r', facecolor='none')
                    ax.add_patch(rect)

                    label_text = f"{label['Name']} ({label['Confidence']:.2f}%)"
                    plt.text(left, top - 2, label_text, color='white', fontsize=10, 
                             bbox=dict(facecolor='red', alpha=0.7))

        plt.axis('off')
        plt.show()

    except Exception as e:
        print(f"Error: {e}")

def main():
    bucket = input("Enter S3 Bucket Name: ").strip()
    photo = input("Enter Image File Name: ").strip()
    detect_labels(photo, bucket)

if __name__ == "__main__":
    main()