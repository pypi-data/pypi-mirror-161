import numpy as np
import pandas as pd 
import cv2
import uuid
import os
import time
import face_recognition
import shutil
import numpy as np
import matplotlib.pyplot as plt
from  matplotlib import image
from scipy import stats
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans


def capturePictures(destination_path = 'CollectedImages/Unknown/'):
    cap=cv2.VideoCapture(0)
    KNOWN_FACE = (0,200,0)
    UNKNOWN_FACE = (0,0,200)
    unknown_faces_encod = np.empty(0)
    unknown_faces_loc = np.empty(0)

    while cap.isOpened(): 
        ret, frame = cap.read()
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for i in range(len(face_locations)):
            fl = face_locations[i]
            x1,y1,x2,y2 = fl[3],fl[0],fl[1],fl[2]
            if cv2.waitKey(10) & 0xFF == ord('p'):
                imgname = os.path.join(destination_path+'{}.jpg'.format(str(uuid.uuid1())))
                unknown_faces_encod = np.append(unknown_faces_encod, np.array(face_encodings[i]))
                unknown_faces_loc = np.append(unknown_faces_loc, np.array(face_locations[i]))
                #Saving image CV2
                cv2.imwrite(imgname, frame)
               
            cv2.rectangle(frame,(x1,y1),(x2,y2),KNOWN_FACE,4)
        cv2.imshow("Capture",frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break
    return unknown_faces_encod, unknown_faces_loc
    
    
def loading_data(data_dir='CollectedImages/Train'):
    images_encodings = np.empty(0)
    images_locations = np.empty(0)
    names = np.empty(0)
    fnames = np.empty(0)
    for item in os.listdir(data_dir):
#         print(item)
        item_path = os.path.join(data_dir, item)
        if os.path.isfile(item_path):
            img = image.imread(item_path)
            face_locations = face_recognition.face_locations(img)
            face_encodings = face_recognition.face_encodings(img, face_locations)
#             print(face_encodings)
#             print(face_locations)
            if len(images_encodings) == 0:
                images_encodings = np.array(face_encodings)
                images_locations = np.array(face_locations)
                fnames = np.append(fnames, np.array(item_path))
                names = np.append(names, np.array(item))
            else:
#                         print(f_path,images_encodings.shape, np.array(face_encodings).shape)
                images_encodings = np.vstack((images_encodings, np.array(face_encodings)))
                images_locations = np.vstack((images_locations, np.array(face_locations)))
                fnames = np.append(fnames, np.array(item_path))
                names = np.append(names, np.array(item))
        else: 
    #         current_cluster_obs = []
            for f in os.listdir(item_path):
                f_path = os.path.join(item_path, f)
                if os.path.isfile(f_path):
                    img = image.imread(f_path)
                    face_locations = face_recognition.face_locations(img)
                    face_encodings = face_recognition.face_encodings(img, face_locations)
                    if len(images_encodings) == 0:
                        images_encodings = np.array(face_encodings)
                        images_locations = np.array(face_locations)
                        fnames = np.append(fnames, np.array(os.path.join(item_path, f)))
                        names = np.append(names, np.array(item))
                    else:
#                         print(f_path,images_encodings.shape, np.array(face_encodings).shape)
                        images_encodings = np.vstack((images_encodings, np.array(face_encodings)))
                        images_locations = np.vstack((images_locations, np.array(face_locations)))
                        fnames = np.append(fnames, np.array(os.path.join(item_path, f)))
                        names = np.append(names, np.array(item))
                        
    return images_encodings, images_locations, names, fnames
    
    
def streamPredictions(model, camera_source=0):
    cap=cv2.VideoCapture(camera_source)
    KNOWN_FACE = (0,200,0)
    UNKNOWN_FACE = (0,0,200)
    unknown_faces_encod = np.empty(0)
    unknown_faces_loc = np.empty(0)

    while cap.isOpened(): 
        ret, frame = cap.read()
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        for i in range(len(face_locations)):
            fl = face_locations[i]
            x1,y1,x2,y2 = fl[3],fl[0],fl[1],fl[2]
#             if cv2.waitKey(10) & 0xFF == ord('p'):
#                 imgname = os.path.join(destination_path+'{}.jpg'.format(str(uuid.uuid1())))
#                 unknown_faces_encod = np.append(unknown_faces_encod, np.array(face_encodings[i]))
#                 unknown_faces_loc = np.append(unknown_faces_loc, np.array(face_locations[i]))
#                 #Saving image CV2
#                 cv2.imwrite(imgname, frame)
            name = model.predict(face_encodings[i])
    #         print(name)
            if name == '???':
                color = UNKNOWN_FACE
            else: 
                color = KNOWN_FACE
            cv2.putText(frame,name,(x1+6, y1+12),cv2.FONT_HERSHEY_COMPLEX,1,color,2)   
            cv2.rectangle(frame,(x1,y1),(x2,y2),color,4)
        cv2.imshow("Capture",frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break
    
    
def move_data(destination_dir='CollectedImages/Unknown'):
    for item in os.listdir(destination_dir):
#         print(item)
        item_path = os.path.join(destination_dir, item)
        if os.path.isfile(item_path):
#             print(item)
            pass
        else: 
            for f in os.listdir(item_path):
                f_path = os.path.join(item_path, f)
                if os.path.isfile(f_path):
                    dest = shutil.move(f_path, destination_dir)
            shutil.rmtree(item_path, ignore_errors=True)