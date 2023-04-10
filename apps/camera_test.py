import cv2


def stream():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    
    while True:
        ret, frame = cap.read()
        
        if ret:
            cv2.imshow("Frame", frame)
        else:
            print("Cannot read")
            cap.release()
            exit()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    stream()
