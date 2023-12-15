import numpy as np
import cv2
import mediapipe as mp
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os

from matplotlib import pyplot as plt
# transformers

# Define actions
actions = ['Move_1', 'Move_2', 'Move_3', 'Move_4']

# Initialize MediaPipe Holistic
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Redefine the mediapipe_detection function within
def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results

# Redefine the draw_styled_landmarks function within ct.py
def draw_styled_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2))

# Redefine the extract_keypoints function within
def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
    return pose


def prob_viz(res, actions, input_frame, colors):
    output_frame = input_frame.copy()
    for num, prob in enumerate(res):
        cv2.rectangle(output_frame, (0, 60 + num * 40), (int(prob * 100), 90 + num * 40), colors[num], -1)
        cv2.putText(output_frame, actions[num], (0, 85 + num * 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)

    return output_frame

# Load the trained model
model_path = os.path.join('models', 'Model_M1toM5.h5')
model = load_model(model_path)

colors = [(245, 117, 16), (117, 245, 16), (16, 117, 245), (200, 117, 16), (250, 245, 16)]

# 1. New detection variables
sequence = []
sentence = []
predictions = []
threshold = 0.5

# Change to your MP4 file path
video_path = 'MP_Data_Video_Input/Test_1.mp4'
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(video_path)

max_seq_length = 30

# Set mediapipe mode
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    res = None  # Initialize res to None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform pose detection
        image, results = mediapipe_detection(frame, holistic)
        draw_styled_landmarks(image, results)

        keypoints = extract_keypoints(results)
        sequence.append(keypoints)
        sequence = sequence[-max_seq_length:]

        if len(sequence) == max_seq_length:
            # Pad the sequence to match the training data
            padded_sequence = pad_sequences([sequence], maxlen=max_seq_length, padding='post', dtype='float32')
            res = model.predict(padded_sequence)[0]
            predictions.append(np.argmax(res))

        if res is not None:
            if np.unique(predictions[-10:])[0] == np.argmax(res):
                if res[np.argmax(res)] > threshold:

                    if len(sentence) > 0:
                        if actions[np.argmax(res)] != sentence[-1]:
                            sentence.append(actions[np.argmax(res)])
                    else:
                        sentence.append(actions[np.argmax(res)])

            if len(sentence) > 5:
                sentence = sentence[-5:]

                # Viz probabilities
            image = prob_viz(res, actions, image, colors)

        cv2.rectangle(image, (0, 0), (640, 40), (245, 117, 16), -1)
        cv2.putText(image, ' '.join(sentence), (3, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Show to screen
        cv2.imshow('OpenCV Feed', image)

        # Break gracefully
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()