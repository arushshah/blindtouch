import numpy as np
import cv2
from matplotlib import pyplot as plt
import glob

def getImg(imgName):
	MIN_MATCH_COUNT = 10
	FLANN_INDEX_KDTREE = 0
	MAX_MATCHES = 0
	MAX_GOOD = []
	MAX_KP1 = None
	MAX_KP2 = None
	MAX_DES1 = None
	MAX_DES2 = None
	# Initiate SIFT detector
	sift = cv2.xfeatures2d.SIFT_create()

	index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
	search_params = dict(checks = 50)

	flann = cv2.FlannBasedMatcher(index_params, search_params)

	img1 = cv2.imread(imgName,0) # trainImage

	IMG2BEST = None
	imgName = ""

	for filepath in glob.iglob('imagesToMatch/*'):
	    img2 = cv2.imread(filepath,0)
	    # find the keypoints and descriptors with SIFT
	    kp1, des1 = sift.detectAndCompute(img1,None)
	    kp2, des2 = sift.detectAndCompute(img2,None)

	    matches = flann.knnMatch(des1,des2,k=2)
	    # store all the good matches as per Lowe's ratio test.
	    good = []
	    for m,n in matches:
		if m.distance < 0.7*n.distance:
		    good.append(m)
	    if (len(good) > MAX_MATCHES):
		MAX_MATCHES = len(good)
		MAX_GOOD = good
		IMG2BEST = img2
		MAX_KP1 = kp1
		MAX_KP2 = kp2
		MAX_DES1 = des1
		MAX_DES2 = des2
		imgName = filepath

	if len(MAX_GOOD)>MIN_MATCH_COUNT:
	    src_pts = np.float32([ MAX_KP1[m.queryIdx].pt for m in MAX_GOOD ]).reshape(-1,1,2)
	    dst_pts = np.float32([ MAX_KP2[m.trainIdx].pt for m in MAX_GOOD ]).reshape(-1,1,2)

	    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
	    matchesMask = mask.ravel().tolist()

	    h,w = img1.shape
	    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
	    dst = cv2.perspectiveTransform(pts,M)

	    img2 = cv2.polylines(IMG2BEST,[np.int32(dst)],True,255,3, cv2.LINE_AA)

	else:
	    print "Not enough matches are found - %d/%d" % (len(MAX_GOOD),MIN_MATCH_COUNT)
	    matchesMask = None


	draw_params = dict(matchColor = (0,255,0), # draw matches in green color
		           singlePointColor = None,
		           matchesMask = matchesMask, # draw only inliers
		           flags = 2)

	img3 = cv2.drawMatches(img1,MAX_KP1,img2,MAX_KP2,MAX_GOOD,None,**draw_params)

	return imgName
	#plt.imshow(img3, 'gray'),plt.show()
