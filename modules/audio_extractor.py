import os
import subprocess
from pydub import AudioSegment

class AudioExtractor:
    def __init__(self, output_dir, sample_rate=16000, channels=1):
        self.output_dir = output_dir
        self.sample_rate = sample_rate
        self.channels = channels
        os.makedirs(output_dir, exist_ok=True)
    
    def extract_audio(self, video_path):
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            str: 提取的音频文件路径
        """
        # 生成输出文件路径
        video_filename = os.path.basename(video_path)
        audio_filename = os.path.splitext(video_filename)[0] + ".wav"
        audio_path = os.path.join(self.output_dir, audio_filename)
        
        try:
            # 使用ffmpeg提取音频并转换为适合语音识别的格式
            print(f"正在从视频提取音频: {video_path}")
            subprocess.run([
                "ffmpeg",
                "-i", video_path,
                "-ar", str(self.sample_rate),  # 采样率
                "-ac", str(self.channels),     # 声道数
                "-f", "wav",
                "-y",  # 覆盖已存在的文件
                audio_path
            ], check=True)
            
            print(f"音频提取完成: {audio_path}")
            return audio_path
        except subprocess.CalledProcessError as e:
            print(f"音频提取失败: {e}")
            raise
    
    def segment_audio(self, audio_path, segment_length_ms=300000):
        """
        将长音频分割成小片段
        
        Args:
            audio_path: 音频文件路径
            segment_length_ms: 每个片段的长度(毫秒)，默认5分钟
            
        Returns:
            list: 分割后的音频片段路径列表
        """
        print(f"正在分割音频: {audio_path}")
        
        # 加载音频文件
        audio = AudioSegment.from_wav(audio_path)
        
        # 分割音频
        segment_paths = []
        base_filename = os.path.splitext(os.path.basename(audio_path))[0]
        
        for i in range(0, len(audio), segment_length_ms):
            # 提取片段
            segment = audio[i:i+segment_length_ms]
            
            # 保存片段
            segment_filename = f"{base_filename}_segment_{i//segment_length_ms+1}.wav"
            segment_path = os.path.join(self.output_dir, segment_filename)
            segment.export(segment_path, format="wav")
            segment_paths.append(segment_path)
        
        print(f"音频分割完成，共 {len(segment_paths)} 个片段")
        return segment_paths