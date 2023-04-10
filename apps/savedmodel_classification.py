import argparse
#import pathlib
import numpy as np
import tensorflow
import PIL.Image
import cv2
import time


class Model:
    def __init__(self, model_dirpath):
        model = tensorflow.saved_model.load(str(model_dirpath))
        self.serve = model.signatures['serving_default']
        self.input_shape = self.serve.inputs[0].shape[1:3]

    def predict(self, image):
        image = PIL.Image.fromarray(image.astype("uint8"), "RGB")
        #image = PIL.Image.open(image_filepath).resize(self.input_shape)
        input_array = np.array(image, dtype=np.float32)[np.newaxis, :, :, :]

        input_tensor = tensorflow.convert_to_tensor(input_array)
        return self.serve(input_tensor)


def parser_outputs(outputs):
    probs = list(outputs.values())[0].numpy().tolist()
    max_score = max(probs[0])
    index_max_score = probs[0].index(max_score)

    return max_score, index_max_score
    #for index, score in enumerate(outputs[0]):
    #    print(f"Label: {index}, score: {score:.5f}")


def main():
    
    model_dirpath = "model"
    model = Model(model_dirpath)

    with open("model/labels.txt", "r") as f:
        content = f.readlines()

    cap = cv2.VideoCapture(0)
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 3.0, (640, 480))
    
    cnt = 0

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Camera NOT opened")
        exit()
        
    color = (0, 0, 0)
    while True:
        ret, frame = cap.read()
        if ret:
            Ts = time.time()
            outputs = model.predict(frame)
            time_pass = time.time() - Ts             

            max_score, index_max_score = parser_outputs(outputs)
            
            name = content[index_max_score].strip()
            if name[0] == "S":
                name = name.replace("S_", "NG_")
                color = (0, 0, 255)
            else:
                name = name.replace("F_", "")
                color = (0, 255, 0)

            text = name + " " + '{:.2%}'.format(max_score) + " fps: " + '{:.2f}'.format(1/time_pass) 
            cv2.putText(frame, text, (30,30), cv2.FONT_HERSHEY_PLAIN, 2, color, 1, cv2.LINE_AA)
            out.write(frame)
            cv2.imshow("Result", frame)
        else:
            print("Image NOT read")
            exit()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
