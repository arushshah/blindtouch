import numpy as np
from google.cloud import vision
import cv2
import os
import glob
import sys
import io

DIM=(1280, 720)
K=np.array([[535.6852457640018, 0.0, 669.2132763083513], [0.0, 534.0036866412527, 354.42099468045143], [0.0, 0.0, 1.0]])
D=np.array([[-0.10233486931782577], [0.22394766572382502], [-0.5845007867009375], [0.3785197455801081]])

def undistort(img_path, balance=0, dim2=None, dim3=None):
    img = cv2.imread(img_path)
    dim1 = img.shape[:2][::-1]  #dim1 is the dimension of input image to un-distort
    assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "Image to undistort needs to have same aspect ratio as the ones used in calibration"
    if not dim2:
        dim2 = dim1
    if not dim3:
        dim3 = dim1
    scaled_K = K * dim1[0] / DIM[0]  # The values of K is to scale with image dimension.
    scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0
    # Thi1280 x 720 s is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3), balance=balance)
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)
    undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return undistorted_img

def label(img_path):
    bounding_boxes = {}
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/arushshah/Downloads/blindassistcloudcreds.json"
    client = vision.ImageAnnotatorClient()

    with io.open(img_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    count = 0
    for text in texts:
        if count == 0:
            count += 1
            continue
        tmp = [vertex for vertex in text.bounding_poly.vertices]
        bounding_boxes[str(text.description)] = tmp

        print("---------------------")
        print(text.description)
        print(tmp)
        print("---------------------")

    return bounding_boxes

if __name__ == '__main__':
    '''
    flattened_images = []
    for p in sys.argv[1:3]:
        flattened_images.append(undistort(p))
    
    print(len(flattened_images))
    for i in flattened_images:
        cv2.imshow("img", i)
        cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imwrite('left.jpg', flattened_images[0])
    cv2.imwrite('right.jpg', flattened_images[1])
    '''
    os.chdir("/home/arushshah/Documents/Research/pipeline/OpenPano-master/src/")
    os.system("./image-stitching ~/Documents/Research/pipeline/left.jpg ~/Documents/Research/pipeline/right.jpg")
    os.system("cp out.jpg /home/arushshah/Documents/Research/pipeline")
    os.chdir("/home/arushshah/Documents/Research/pipeline/")
    bounding_boxes = label("/home/arushshah/Documents/Research/pipeline/out.jpg")

    img = cv2.imread('out.jpg',cv2.IMREAD_COLOR)

    print("\n" + "------------------------")
    count = 0
    for vertex in bounding_boxes:
        print(str(vertex))
        start_point = (bounding_boxes[str(vertex)][0].x, bounding_boxes[str(vertex)][0].y)
        end_point = (bounding_boxes[str(vertex)][2].x, bounding_boxes[str(vertex)][2].y)
        color = (0, 255, 0) 
        img = cv2.rectangle(img, start_point, end_point, color, 2) 
        cv2.putText(img, str(vertex), end_point, cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), lineType=cv2.LINE_AA)
        

    img = cv2.resize(img, (1280, 720))
    cv2.imshow("img", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

