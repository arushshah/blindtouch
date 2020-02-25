import numpy as np
import argparse
import imutils
import glob
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--template", required=True, help="Path to template image")
ap.add_argument("-i", "--images", required=True,
	help="Path to images where template will be matched")
ap.add_argument("-v", "--visualize",
	help="Flag indicating whether or not to visualize each iteration")
args = vars(ap.parse_args())

template = cv2.imread(args["template"])
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
template = cv2.Canny(template, 50, 200)
(tH, tW) = template.shape[:2]
cv2.imshow("Template", template)

maxScore = 0
maxImagePath = ""

for imagePath in glob.glob(args["images"] + "/*.jpg"):
	
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found = None
	
    for scale in np.linspace(0.2, 1.0, 20)[::-1]:
		
		resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
		r = gray.shape[1] / float(resized.shape[1])
		
		if resized.shape[0] < tH or resized.shape[1] < tW:
			break
        
		edged = cv2.Canny(resized, 50, 200)
		result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
		(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
		
		if args.get("visualize", False):
		
			clone = np.dstack([edged, edged, edged])
			cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
				(maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
			cv2.imshow("Visualize", clone)
			cv2.waitKey(0)
		
		if found is None or maxVal > found[0]:
			found = (maxVal, maxLoc, r)

    (maxVal, maxLoc, r) = found
    if (maxVal > maxScore):
        maxScore = maxVal
        (finalMaxVal, finalMaxLoc, finalR) = found
        maxImagePath = imagePath

image = cv2.imread(maxImagePath)
(startX, startY) = (int(finalMaxLoc[0] * finalR), int(finalMaxLoc[1] * finalR))
(endX, endY) = (int((finalMaxLoc[0] + tW) * finalR), int((finalMaxLoc[1] + tH) * finalR))

cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
cv2.imwrite("output.jpg", image)