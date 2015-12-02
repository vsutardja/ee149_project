import numpy as np
import cv2

IMAGE_PATH = 'img/contourTest.png'

image = cv2.imread(IMAGE_PATH)

lower_bound = np.array([0, 0, 100], np.uint8)
upper_bound = np.array([50, 50, 255], np.uint8)

mask = cv2.inRange(image, lower_bound, upper_bound)
output = cv2.bitwise_and(image, image, mask = mask)
img = mask

# cv2.imshow("images", np.hstack([image, output]))
cv2.imshow("images", mask)

contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

largest_contour = contours[0]
largest_area = cv2.contourArea(contours[0])

for contour in contours:
	area = cv2.contourArea(contour)
	if area > largest_area:
		largest_contour = contour
		largest_area = area

# cv2.drawContours(image, [largest_contour], 0, (255, 0, 0), 1)
# cv2.imshow("images", image)

M = cv2.moments(largest_contour)
cx = int(M['m10']/M['m00'])
cy = int(M['m01']/M['m00'])
cv2.circle(image, (cx, cy), 3, (0, 255, 0))
cv2.imshow("images", np.hstack([output, image]))
cv2.waitKey(0)
