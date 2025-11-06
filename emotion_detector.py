import cv2
from deepface import DeepFace

def detect_emotion(frame):
    """
    Detects the dominant emotion from a webcam frame using DeepFace.
    Returns the emotion label (e.g., 'happy', 'sad', 'neutral', etc.)
    """
    try:
        # Analyze the frame
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]['dominant_emotion']
        return dominant_emotion

    except Exception as e:
        print(f"Emotion detection error: {e}")
        return "unknown"

def emotion_response(emotion):
    """
    Returns a friendly message based on detected emotion.
    """
    responses = {
        "happy": "You're glowing today 😄",
        "sad": "Hey, don’t be sad — your smile lights up the room 😊",
        "angry": "Deep breaths... peace mode activated 🧘",
        "surprise": "Whoa! What happened?! 👀",
        "fear": "Don’t worry, you’ve got this 💪",
        "neutral": "You look calm and focused 🧠",
        "disgust": "Maybe a coffee break? ☕",
        "unknown": "Hmm, can’t read that face right now 🤔"
    }
    return responses.get(emotion, "Stay awesome!")
