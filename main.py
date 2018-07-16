# USAGE
# python main.py -p persons -v videos/test_video.mp4

import face_recognition
import cv2
from imutils import paths
import argparse
import os

def find_faces_in_video(personsPath, videoPath):
    # This is a demo of running face recognition on a video file and saving the results to a new video file.
    #
    # PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
    # OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
    # specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

    # Open the input movie file
    input_movie = cv2.VideoCapture(videoPath)
    length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))

    ret, frame = input_movie.read()
    FrameSize=(frame.shape[1], frame.shape[0])

    # Create an output movie file (make sure resolution/frame rate matches input video!)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    head, tail = os.path.split(videoPath)
    tail = tail.split('.', 1)[0]
    output_movie = cv2.VideoWriter('outputs/' + tail + '.avi', fourcc, 20.0, FrameSize)

    # Load some sample pictures and learn how to recognize them.
    known_faces = []
    labels = []
    for imagePath in paths.list_files(personsPath, validExts=(".png")):
        image = face_recognition.load_image_file(imagePath)
        face_encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(face_encoding)
        labels.append(imagePath.split("/")[-2])

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    frame_number = 0
    #length = 100
    while frame_number < length:
        
        # Grab a single frame of video
        ret, frame = input_movie.read()
        frame_number += 1

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        try:
            rgb_frame = frame[:, :, ::-1]
        except:
            frame_number+=1
            print("Writing frame {} / {}".format(frame_number, length))
            continue

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.60)
          
            # If you had more than 2 faces, you could make this logic a lot prettier
            # but frame_counter kept it simple for the demo
            try:
                name = labels[match.index(True)]
                face_names.append(name)
            except:
                continue

        # Label the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            if not name:
                continue

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

        # Write the resulting image to the output video file
        print("Writing frame {} / {}".format(frame_number, length))
        output_movie.write(frame)
    # All done!
    input_movie.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--persons", required=True, help="path to persons' images dataset")
    ap.add_argument("-v", "--video", required=True, help="path of video")
    args = vars(ap.parse_args())
    find_faces_in_video(args["persons"], args["video"])