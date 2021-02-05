import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while True:
    ret, img = cap.read()
    cv2.imshow("camera", img)
    if cv2.waitKey(10) == 27: # Клавиша Esc? А как по крестику выходить?
        break
    if cv2.getWindowProperty('window-name', 0) >= 0:
        break
cap.release()
cv2.destroyAllWindows()
