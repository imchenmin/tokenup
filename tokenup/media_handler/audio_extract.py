from moviepy.editor import VideoFileClip
def extract_audio(video_file_str, output_audio_path):
    try:
        video_clip = VideoFileClip(video_file_str)
        audio_clip = video_clip.audio
        # , codec='mp3', fps=44100, bitrate='320k'
        audio_clip.write_audiofile(output_audio_path)
        audio_clip.close()
        video_clip.close()
        return True, "音频提取成功！"
    except Exception as e:
        return False, f"提取音频时出错：{str(e)}"