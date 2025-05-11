import os
import json
from datetime import timedelta
from modules.text_processor_improved import TextProcessor

class TranscriptGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.text_processor = TextProcessor()
    
    def generate(self, recognition_results, base_filename, formats=None):
        """
        生成文字稿
        
        Args:
            recognition_results: 语音识别结果列表
            base_filename: 基础文件名(不含扩展名)
            formats: 输出格式列表，支持 "txt", "srt", "json"
            
        Returns:
            dict: 生成的文件路径字典
        """
        if formats is None:
            formats = ["txt", "srt"]
        
        # 合并所有识别结果
        all_text = ""
        all_segments = []
        
        for result in recognition_results:
            # 确保 result 是字典并且包含 'text' 键，且值不为 None
            if isinstance(result, dict) and 'text' in result and result["text"] is not None:
                # 确保 text 是字符串类型
                if isinstance(result["text"], str):
                    all_text += result["text"] + " "
                else:
                    # 如果 text 不是字符串，可以选择跳过或记录日志
                    print(f"警告: 识别结果中的 'text' 字段不是字符串，已跳过: {result}")
            else:
                # 如果 result 格式不正确或 text 为 None，可以选择跳过或记录日志
                print(f"警告: 无效的识别结果或 'text' 字段为 None，已跳过: {result}")

            # 如果有分段信息，添加到总段落列表
            if isinstance(result, dict) and "segments" in result and result["segments"]:
                # 计算时间偏移(如果需要)
                time_offset = 0
                if all_segments:
                    time_offset = all_segments[-1]["end"]
                
                # 添加段落，并应用时间偏移
                for segment in result["segments"]:
                    all_segments.append({
                        "text": segment["text"],
                        "start": segment["start"] + time_offset,
                        "end": segment["end"] + time_offset
                    })
        
        # 生成各种格式的文件
        output_files = {}
        
        if "txt" in formats:
            # 处理文本以提高可读性
            processed_text = all_text.strip()
            # 只有在 processed_text 非空时才进行处理
            if processed_text:
                try:
                    # 修正常见错误
                    processed_text = self.text_processor.correct_common_errors(processed_text)
                    # 添加标点和分段
                    processed_text = self.text_processor.process(processed_text)
                except Exception as e:
                    print(f"文本处理时发生错误: {e}")
                    # 保留原始合并文本作为后备
                    processed_text = all_text.strip()
            else:
                print("警告: 合并后的文本为空，无法生成 TXT 文件内容。")
                processed_text = "" # 确保为空字符串
            
            txt_path = os.path.join(self.output_dir, f"{base_filename}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(processed_text)
            output_files["txt"] = txt_path
        
        if "srt" in formats and all_segments:
            srt_path = os.path.join(self.output_dir, f"{base_filename}.srt")
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(self._generate_srt(all_segments))
            output_files["srt"] = srt_path
        
        if "json" in formats:
            json_path = os.path.join(self.output_dir, f"{base_filename}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump({
                    "text": all_text.strip(),
                    "segments": all_segments
                }, f, ensure_ascii=False, indent=2)
            output_files["json"] = json_path
        
        return output_files
    
    def _generate_srt(self, segments):
        """生成SRT格式字幕文件内容"""
        srt_content = ""
        
        for idx, segment in enumerate(segments, 1):
            start_time = self._format_time(segment["start"])
            end_time = self._format_time(segment["end"])
            
            srt_content += f"{idx}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{segment['text']}\n\n"
        
        return srt_content
    
    def _format_time(self, seconds):
        """将秒数格式化为SRT时间格式 (HH:MM:SS,mmm)"""
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int(td.microseconds / 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"