
import ffmpeg
import os
import json

def extract_audio(video_path, output_audio_path):
    """
    从视频文件中提取音频并保存为wav。
    参数:
    video_path (str): 视频文件的路径。
    output_audio_path (str): 输出音频文件的路径。
    """
    if not os.path.exists(video_path):
        raise "{} not find".format(video_path)
    if  os.path.exists(output_audio_path):
        os.remove(output_audio_path)
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_audio_path, acodec='mp3', audio_bitrate='320k')
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        raise e

def merge_subtitles_to_video(video_path, subtitle_path, output_video_path):
    """
    将字幕文件合并到视频文件中。
    参数:
    video_path (str): 视频文件的路径。
    subtitle_path (str): 字幕文件的路径。
    output_video_path (str): 合并字幕后的输出视频文件的路径。
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"{video_path} not found")
    if not os.path.exists(subtitle_path):
        raise FileNotFoundError(f"{subtitle_path} not found")
    if os.path.exists(output_video_path):
        os.remove(output_video_path)
    
    subtitle_path = subtitle_path.replace("\\", "/")
    print("subtitle_path = {}".format(subtitle_path))
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_video_path, vf=f"subtitles={subtitle_path}")
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to merge subtitles into video: {e}")

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.remove(file_path)
    print("清空文件夹：{}".format(folder_path))



def import_config_file(file):
    if file is not None:
        content = file.read()
        try:
            json_data = json.loads(content)
            return json_data  
        except Exception as e:
            raise e
            
if __name__ == "__main__":
    pass