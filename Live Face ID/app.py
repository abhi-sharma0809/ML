from flask import Flask, render_template, Response
import cv2
import face_recognition
import os

app = Flask(__name__)

# Load known faces and their embeddings
known_faces = {}
attendence = set()

for filename in os.listdir("DATABASE"):
    if filename.endswith('.jpg'):
        img_path = os.path.join("DATABASE", filename)
        known_image = face_recognition.load_image_file(img_path)
        face_encodings = face_recognition.face_encodings(known_image)
        if face_encodings:
            known_faces[filename[:-4]] = face_encodings[0]

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        success, img = cap.read()
        if not success:
            continue

        # Find all face locations and face encodings in the current frame
        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            best_match = None
            highest_similarity = 1.0  # Set to 1.0 as face_distance returns a similarity measure (lower is better)

            for name, known_encoding in known_faces.items():
                similarity = face_recognition.face_distance([known_encoding], face_encoding)
                if similarity < highest_similarity:
                    highest_similarity = similarity
                    best_match = name

            if best_match:
                attendence.add(best_match)
                cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(img, best_match, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance')
def get_attendance():
    return {'attendance': list(attendence)}

if __name__ == "__main__":
    app.run(debug=True)
