import classify
import sys
import cv2
import preprocess
import time

classifier = classify.Classify()
preprocessor = preprocess.PreProcessor()

camera = cv2.VideoCapture(0)
i = 0;
start = time.time()
while True:
    return_value, image = camera.read()
    cv2.imwrite('opencv'+str(i)+'.png', image)
    bb = (preprocessor.align('opencv'+str(i)+'.png'))
    cv2.rectangle(image, (bb[0],bb[1]), (bb[2],bb[3]), (0, 255, 0), 5)
    name = classifier.predict('temp.png')
    font = cv2.FONT_HERSHEY_SIMPLEX 
    cv2.putText(image, name, (50, 50), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow('frame',image)
    cv2.imwrite('opencv'+str(i)+'.png', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    i+=1
end_time = time.time()
print(i/(end_time-start))

# When everything done, release the capture
camera.release()
cv2.destroyAllWindows()
print(classifier.predict('temp.png'))
