import numpy as np
import cv2
import matplotlib.pyplot as plt

IMAGE_PATH = 'img/file%d.png'

x_vals = []
y_vals = []
for i in range(1,9):
    print i
    image = cv2.imread(IMAGE_PATH % i)

    lower_bound = np.array([0, 0, 100], np.uint8)
    upper_bound = np.array([50, 50, 255], np.uint8)

    mask = cv2.inRange(image, lower_bound, upper_bound)
    output = cv2.bitwise_and(image, image, mask = mask)
    img = mask

# cv2.imshow("images", np.hstack([image, output]))
    #cv2.imshow("images", mask)
    #cv2.imwrite("thresh_img/detect%d.png" % i, img)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if len(contours) == 0:
        continue
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
    if M['m00'] == 0:
        continue
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    cv2.circle(image, (cx, cy), 3, (0, 255, 0))
    x_vals.append(cx)
    y_vals.append(cy)
    cv2.imshow("images", np.hstack([output, image]))
    #cv2.imwrite("thresh_img/pic%d.png" % i, np.hstack([output, image]))
    cv2.waitKey(0)

y_vals = map((lambda y : 480-y), y_vals)
plt.hold(True)
plt.scatter(x_vals, y_vals, color='red')
plt.plot(x_vals, y_vals)
#plt.show()
plt.savefig('thresh_img/path.png')
with open ('data_file', 'w') as data_file:
    data_file.write(str(x_vals) + '\n')
    data_file.write(str(y_vals) + '\n')
