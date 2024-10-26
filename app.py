import ffmpeg
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from speech_recognition import Recognizer, AudioFile

def filter_scenes(scene_list, min_duration=10.0):
    """ Filter scenes shorter than a minimum duration in seconds. """
    filtered_scenes = []
    for scene in scene_list:
        start_time = scene[0].get_seconds()
        end_time = scene[1].get_seconds()
        duration = end_time - start_time
        if duration >= min_duration:
            filtered_scenes.append((start_time, end_time))
    return filtered_scenes

def extract_audio(video_path, start_time, end_time, output_audio_path="temp_audio.wav"):
    """ Extract audio from video for a specific time range. """
    ffmpeg.input(video_path, ss=start_time, to=end_time).output(output_audio_path).run()
    return output_audio_path

def detect_dialogue(audio_file):
    """ Use speech recognition to detect dialogue in the audio. Returns True if dialogue is detected. """
    recognizer = Recognizer()
    with AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            transcript = recognizer.recognize_google(audio)
            if len(transcript) > 10:  # Assume meaningful dialogue if there's more than a few words
                return True
        except:
            return False
    return False

def process_video(video_path, min_scene_duration=10.0):
    """ Process the video to detect and extract meaningful storytelling scenes. """
    # Step 1: Scene Detection
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector())
    video_manager.start()

    # Detect scenes
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()

    print(f"Detected {len(scene_list)} scenes in the video.")

    # Step 2: Filter short scenes
    filtered_scenes = filter_scenes(scene_list, min_duration=min_scene_duration)
    print(f"Filtered to {len(filtered_scenes)} scenes longer than {min_scene_duration} seconds.")

    # Step 3: Check each scene for dialogue
    final_scenes = []
    for i, (start_time, end_time) in enumerate(filtered_scenes):
        print(f"Processing Scene {i+1}: Start {start_time} / End {end_time}")
        
        # Extract the audio for this scene
        audio_file = extract_audio(video_path, start_time, end_time)

        # Detect dialogue
        if detect_dialogue(audio_file):
            print(f"Dialogue detected in Scene {i+1}. Adding to final list.")
            final_scenes.append((start_time, end_time))
        else:
            print(f"No dialogue in Scene {i+1}. Skipping.")

    # Step 4: Extract final video segments with storytelling
    for i, (start_time, end_time) in enumerate(final_scenes):
        output_clip = f"story_segment_{i+1}.mp4"
        ffmpeg.input(video_path, ss=start_time, to=end_time).output(output_clip).run()
        print(f"Extracted story segment {i+1}: {output_clip}")

# Example Usage
video_path = input("Please enter the video path: ")
process_video(video_path, min_scene_duration=30.0)