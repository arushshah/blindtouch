from google.cloud import vision
import io
import sys
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/arushshah/Downloads/blindassistcloudcreds.json"
client = vision.ImageAnnotatorClient()

path = sys.argv[1]
with io.open(path, 'rb') as image_file:
    content = image_file.read()

image = vision.types.Image(content=content)

response = client.text_detection(image=image)
texts = response.text_annotations
print('Texts:')

for text in texts:
    print('\n"{}"'.format(text.description))

    vertices = (['({},{})'.format(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices])

    print('bounds: {}'.format(','.join(vertices)))
