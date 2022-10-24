import cv2
import pytesseract

img = cv2.imread('img/fab-lentz-mRMQwK513hY-unsplash.jpg')

text = pytesseract.image_to_string(img)
print(text)