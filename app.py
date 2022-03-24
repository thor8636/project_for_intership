
from azure.storage.blob import BlobServiceClient
from flask import Flask, request, redirect, render_template
import cv2
import numpy as np
import face_recognition
import urllib.request

app = Flask(__name__)


connect_str = "DefaultEndpointsProtocol=https;AccountName=facedata89;AccountKey=lIHa4MyPwZS37XxJ2X7O+eqtGGbUUpnYGFSzBnJ2WEU8RkC7GSHNudBjOTumTwpLeFuAXnTK4ZyB+AStkvqPfA==;EndpointSuffix=core.windows.net"
container_name = "photos"
blob_service_client = BlobServiceClient.from_connection_string(conn_str=connect_str)
try:
    container_client = blob_service_client.get_container_client(container=container_name)
    container_client.get_container_properties() 
except Exception as e:
    print(e)
    print("Creating container...")
    container_client = blob_service_client.create_container(container_name)



@app.route('/')
def home_page():
    image_links = []
    blob_items = container_client.list_blobs()   
    for blob in blob_items:
        blob_client = container_client.get_blob_client(blob=blob.name)
        image_links.append(blob_client.url)
    
    return render_template('home.html', image_links = image_links)


@app.route("/upload-photos", methods=["POST"])
def upload_photos():
    filenames = ""

    for file in request.files.getlist("photos"):
        try:
            container_client.upload_blob(file.filename, file)
            filenames += file.filename + "<br /> "
        except Exception as e:
            print(e)
            print("Ignoring duplicate filenames") 
            
    return redirect('/') 


@app.route("/delete/<path:image>")
def delete(image):
     
    blob_items = container_client.list_blobs()
    image = image

    response = urllib.request.urlopen(image)
    img = face_recognition.load_image_file(response)
    img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgface_encoding = face_recognition.face_encodings(img)[0]
    imgface_encodings = [imgface_encoding,imgface_encoding]
    face_locations = []
    face_encodings = []
    camera = cv2.VideoCapture(0)

    while True:
        ret, frame = camera.read()
        faces = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        faces = cv2.cvtColor(faces, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(faces)
        face_encodings = face_recognition.face_encodings(faces, face_locations)
        

        for encodeFace, faceLoc in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(encodeFace, imgface_encodings)
            faceDis = face_recognition.face_distance(encodeFace, imgface_encodings)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
               name = "Face matched veryfication Successful!!! press q on the keyboard to Exit Webcam"
               y1, x2, y2, x1 = faceLoc
               y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
               cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
               cv2.rectangle(frame, (x1, y2), (x2, y2), (0, 255, 0), cv2.FILLED)
               cv2.putText(frame, name, (x1 - 136, y2 + 14), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
               for blob in blob_items:
                blob_client = container_client.get_blob_client(blob=blob.name)
                if (blob_client.url)  == (image):
                  container_client.delete_blobs(blob.name)

            else:
               name1 = "Face not matched veryfication Unsuccessful!!! press q on the keyboard to Exit Webcam"
               y1, x2, y2, x1 = faceLoc
               y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
               cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
               cv2.rectangle(frame, (x1, y2), (x2, y2), (0, 255, 0), cv2.FILLED)
               cv2.putText(frame, name1, (x1 - 136, y2 + 14), cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 2)
         
        cv2.imshow('Webcam (Press q to exist)', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
           break
    camera.release()
    cv2.destroyAllWindows()        

    return redirect('/') 

if __name__=='__main__':
    app.run()
