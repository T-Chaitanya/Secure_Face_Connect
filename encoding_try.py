import pickle
import face_recognition
import os
known_face_encodings=[]
known_face_names=[]
root_folder=r"images\\"
for root, dirs, files in os.walk(root_folder):
    for file in files:
        try:
            face_name=root.split("\\")[-1]
            var_image = face_recognition.load_image_file(root+"/"+file)
            var_face_encoding = face_recognition.face_encodings(var_image)[0]
            known_face_encodings.append(var_face_encoding)
            known_face_names.append(face_name)
        except:
            print(root+"/"+file)
print(known_face_names)
if os.path.exists("face_encoding_data"):
  os.remove("face_encoding_data")
known_face_list=[known_face_encodings,known_face_names]
dbfile=open("face_encoding_data","ab")
pickle.dump(known_face_list,dbfile)
dbfile.close()

