## Authors
## @Uluc Furkan Vardar
## @Ilkay Tevfik Devran


# USAGE
# python main.py -p persons -v videos/test_video.mp4

import face_recognition
import cv2
from imutils import paths
import argparse
import os


## with using resizeing ? or not 
isResize = True
resize_cofficent = 0.25

#recognation tolarance rate
tolerance_rate=0.46

frame_increment = 3




def load_video_from_path (videoPath):
	input_movie = cv2.VideoCapture(videoPath)
	length = int(input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
	return input_movie,length

def make_it_reSize (frame):
	small_frame= cv2.resize(frame, (0, 0), fx=resize_cofficent, fy=resize_cofficent )
	return small_frame

def get_frame_infos_from_video (input_movie):
	ret, frame = input_movie.read()
	if isResize == True:
		frame = make_it_reSize( frame )
	FrameSize=(frame.shape[1], frame.shape[0])
	return ret ,frame , FrameSize

def create_output_AVI(videoPath , FrameSize ):
	fourcc = cv2.VideoWriter_fourcc(*'MJPG')
	head, tail = os.path.split(videoPath)
	tail = tail.split('.', 1)[0]
	output_movie = cv2.VideoWriter('outputs/' + tail + '.avi', fourcc, 20.0, FrameSize)
	return output_movie

def take_the_sample_pictures_of_the_people( personsPath ):
	known_faces_encodings = []
	known_faces_names = []
	for imagePath in paths.list_files(personsPath, validExts=(".png")):
		image = face_recognition.load_image_file(imagePath)
		face_encoding = face_recognition.face_encodings(image)[0]
		known_faces_encodings.append(face_encoding)
		known_faces_names.append(imagePath.split("/")[-2])
	return known_faces_encodings , known_faces_names

def transform_frame_2_rgb(frame):
	try:
		return frame[:, :, ::-1]
	except:
		print "hata"
		return None

def recognize_people_from_the_frame(face_encodings, known_faces_encodings,known_faces_names ):
	face_names = []
	for face_encoding in face_encodings:
		# See if the face is a match for the known face(s)
		match = face_recognition.compare_faces(known_faces_encodings, face_encoding, tolerance=tolerance_rate)
		try:
			name = known_faces_names[match.index(True)]
			face_names.append(name)
			print "******taninan insan var !*********",name
		except:
			print "**********************************taninma hatasi"
			continue
	return face_names

def put_regs_2_frame_on_people(frame, face_locations, face_names):
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

def find_faces_in_video(personsPath, videoPath):
	input_movie, length_of_the_video = load_video_from_path ( videoPath )
	ret, frame, FrameSize = get_frame_infos_from_video ( input_movie )
	output_movie = create_output_AVI ( videoPath, FrameSize )
	known_faces_encodings, known_faces_names = take_the_sample_pictures_of_the_people(personsPath)
	# Initialize some variables

	face_locations = []
	face_encodings = []
	face_names = []
	frame_number = 0
	#length = 100
	while frame_number < length_of_the_video -1 :
		# Grab a single frame of video
		for i in range (0,frame_increment):
			ret, frame = input_movie.read()
		frame_number += frame_increment
		if isResize == True:
			frame = make_it_reSize(frame)
		rgb_frame = transform_frame_2_rgb(frame)
		if len (rgb_frame) == 1 :
			if rgb_frame == None:
				frame_number+=1
				continue

		# Find all the faces and face encodings in the current frame of video
		face_locations = face_recognition.face_locations(rgb_frame)
		face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
		#print len(face_encodings),"face encodings number"
		face_names = recognize_people_from_the_frame(face_encodings , known_faces_encodings,known_faces_names)
		put_regs_2_frame_on_people(frame, face_locations, face_names)
		
		# Write the resulting image to the output video file
		print("Writing frame {} / {}".format(frame_number, length_of_the_video))
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


