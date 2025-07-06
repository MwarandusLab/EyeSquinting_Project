import cv2
import mediapipe as mp
import numpy as np

# Mediapipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
drawing_utils = mp.solutions.drawing_utils

# Eye landmark indices (for both left and right eyes)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def get_eye_aspect_ratio(landmarks, eye_indices, image_width, image_height):
    # Convert normalized landmarks to pixel coordinates
    coords = [(int(landmarks[i].x * image_width), int(landmarks[i].y * image_height)) for i in eye_indices]

    # Compute vertical distances
    vertical1 = np.linalg.norm(np.array(coords[1]) - np.array(coords[5]))
    vertical2 = np.linalg.norm(np.array(coords[2]) - np.array(coords[4]))
    # Compute horizontal distance
    horizontal = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))

    # Eye Aspect Ratio (EAR)
    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear

# Start video capture
cap = cv2.VideoCapture(1)  # Change index if using a different camera

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("⚠️ Failed to capture frame")
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Calculate EAR for both eyes
            left_ear = get_eye_aspect_ratio(face_landmarks.landmark, LEFT_EYE, w, h)
            right_ear = get_eye_aspect_ratio(face_landmarks.landmark, RIGHT_EYE, w, h)
            avg_ear = (left_ear + right_ear) / 2.0

            # Show EAR value
            cv2.putText(frame, f"Squint Level (EAR): {avg_ear:.2f}", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Optional: draw eyes for visualization
            for idx in LEFT_EYE + RIGHT_EYE:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                cv2.circle(frame, (x, y), 2, (255, 0, 255), -1)

    cv2.imshow("Eye Squint Detector", frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
