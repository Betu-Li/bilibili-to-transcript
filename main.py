#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
B站视频转文字稿程序
"""

import os
import sys
import argparse
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 检查并安装必要的依赖
def check_dependencies():
    try:
        import jieba
    except ImportError:
        print("正在安装jieba分词库...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "jieba"])
        print("jieba安装完成")

from modules.video_downloader import VideoDownloader
from modules.audio_extractor import AudioExtractor
from modules.speech_recognizer import SpeechRecognizer
from modules.transcript_generator import TranscriptGenerator
import config

def main():
    # 检查并安装依赖
    check_dependencies()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="将B站视频转换为文字稿")
    parser.add_argument("url", nargs="?", help="B站视频链接或BV号")
    parser.add_argument("--engine", choices=["vosk", "aliyun", "tencent"], 
                        default=config.RECOGNITION_ENGINE, help="语音识别引擎")
    parser.add_argument("--formats", nargs="+", choices=["txt", "srt", "json"], 
                        default=["txt", "srt"], help="输出格式")
    parser.add_argument("--skip-download", action="store_true", 
                        help="跳过视频下载(需提供视频路径)")
    parser.add_argument("--video-path", help="本地视频路径(与--skip-download一起使用)")
    parser.add_argument("--cookies", help="cookies文件路径(用于下载需要登录的视频)")
    parser.add_argument("--improve-readability", action="store_true", default=True,
                        help="改善文本可读性(添加标点、分段落等)")
    parser.add_argument("--text-correction", action="store_true",default=config.TEXT_CORRECTION_ENABLED, 
                        help="启用文本纠错功能")
    parser.add_argument("--correction-model", choices=["kenlm", "bert", "macbert", "t5"], 
                        default=config.TEXT_CORRECTION_MODEL, help="文本纠错使用的模型")
    args = parser.parse_args()
    
    # 如果没有提供视频链接，交互式输入BV号
    if not args.url and not args.skip_download:
        print("请输入B站视频的BV号:")
        bv_number = input("> ")
        # 确保BV号不为空
        if not bv_number.strip():
            print("错误: BV号不能为空")
            return 1
            
        if bv_number.startswith("BV"):
            args.url = f"https://www.bilibili.com/video/{bv_number}"
        else:
            args.url = f"https://www.bilibili.com/video/BV{bv_number}"
            
        print(f"处理视频: {args.url}")
        
    # 确保URL不为空
    if not args.url and not args.skip_download:
        print("错误: 必须提供视频链接或BV号")
        return 1
    
    start_time = time.time()
    print("=== B站视频转文字稿程序 ===")
    
    try:
        # 1. 下载视频
        video_path = None
        if args.skip_download:
            if not args.video_path or not os.path.exists(args.video_path):
                raise ValueError("跳过下载时必须提供有效的视频路径")
            video_path = args.video_path
            print(f"跳过下载，使用本地视频: {video_path}")
        else:
            # 确保URL不为空且格式正确
            if not args.url:
                raise ValueError("必须提供有效的B站视频链接或BV号")
                
            # 如果只输入了BV号，转换为完整URL
            if args.url.startswith("BV") and "/" not in args.url:
                args.url = f"https://www.bilibili.com/video/{args.url}"
                
            print(f"开始下载视频: {args.url}")
            downloader = VideoDownloader(config.DOWNLOAD_DIR, cookies_path=args.cookies)
            video_path = downloader.download(args.url)
            
            if not video_path or not os.path.exists(video_path):
                raise ValueError("视频下载失败，请检查视频链接是否有效或尝试提供cookies文件")
        
        # 2. 提取音频
        extractor = AudioExtractor(
            config.AUDIO_DIR,
            sample_rate=config.AUDIO_SAMPLE_RATE,
            channels=config.AUDIO_CHANNELS
        )
        audio_path = extractor.extract_audio(video_path)
        
        # 3. 分割音频
        audio_segments = extractor.segment_audio(
            audio_path, 
            segment_length_ms=config.SEGMENT_LENGTH_MS
        )
        
        # 4. 语音识别
        recognizer_kwargs = {}
        if args.engine == "vosk":
            recognizer_kwargs = {"model_path": config.VOSK_MODEL_PATH}
        elif args.engine == "aliyun":
            recognizer_kwargs = {
                "access_key": config.ALIYUN_ACCESS_KEY,
                "access_secret": config.ALIYUN_ACCESS_SECRET,
                "app_key": config.ALIYUN_APPKEY
            }
        elif args.engine == "tencent":
            recognizer_kwargs = {
                "secret_id": config.TENCENT_SECRET_ID,
                "secret_key": config.TENCENT_SECRET_KEY
            }
        
        recognizer = SpeechRecognizer(args.engine, **recognizer_kwargs)
        
        # 识别每个音频片段
        recognition_results = []
        for segment_path in audio_segments:
            result = recognizer.recognize(segment_path)
            recognition_results.append(result)
        
        # 5. 文本处理和纠错
        from modules.text_processor import TextProcessor
        
        # 初始化文本处理器
        text_processor = TextProcessor()
        
        # 如果启用了文本纠错功能
        if args.text_correction:
            try:
                from modules.text_corrector import TextCorrector
                print(f"\n正在初始化文本纠错功能，使用模型: {args.correction_model}")
                corrector = TextCorrector(model_name=args.correction_model)
                
                # 对识别结果进行纠错处理
                for i, result in enumerate(recognition_results):
                    if 'text' in result and result['text'] is not None:
                        print(f"\n正在对第{i+1}段文本进行纠错...")
                        result['text'] = corrector.correct(result['text'])
                    elif 'text' not in result or result['text'] is None:
                        print(f"警告: 第{i+1}段文本识别结果为空，跳过纠错处理")
                        # 确保result['text']存在且不为None
                        if 'text' not in result:
                            result['text'] = ""
                        elif result['text'] is None:
                            result['text'] = ""
                print("文本纠错处理完成")
            except Exception as e:
                print(f"文本纠错初始化失败: {e}")
                print("将继续处理，但不进行文本纠错")
        
        # 6. 生成文字稿
        base_filename = os.path.splitext(os.path.basename(video_path))[0]
        
        # 检查识别结果是否有效
        valid_results = []
        for i, result in enumerate(recognition_results):
            # 创建结果的副本，避免修改原始数据
            valid_result = result.copy() if isinstance(result, dict) else {}
            
            # 确保text字段存在且为有效字符串
            if isinstance(result, dict) and 'text' in result and result['text'] is not None and isinstance(result['text'], str) and result['text'].strip() != "":
                valid_result['text'] = result['text']
                # 复制其他必要字段
                if 'start' in result: valid_result['start'] = result['start']
                if 'end' in result: valid_result['end'] = result['end']
                valid_results.append(valid_result)
            else:
                print(f"警告: 第{i+1}段文本识别结果无效，将被跳过或替换为占位符")
                # 如果有时间信息，添加占位符文本
                if isinstance(result, dict) and 'start' in result and 'end' in result:
                    valid_result['text'] = "[无识别结果]"
                    valid_result['start'] = result['start']
                    valid_result['end'] = result['end']
                    valid_results.append(valid_result)
        
        if not valid_results:
            print("错误: 所有识别结果均无效，无法生成文字稿")
            return 1
            
        print(f"有效识别结果数量: {len(valid_results)}/{len(recognition_results)}")
        
        generator = TranscriptGenerator(config.TRANSCRIPT_DIR)
        output_files = generator.generate(
            valid_results,
            base_filename,
            formats=args.formats
        )
        
        # 7. 输出结果
        print("\n=== 处理完成 ===")
        print(f"总耗时: {time.time() - start_time:.2f} 秒")
        print("生成的文件:")
        for fmt, path in output_files.items():
            print(f"- {fmt.upper()}: {path}")
            
        # 显示使用的功能
        print("\n使用的功能:")
        print(f"- 语音识别引擎: {args.engine}")
        print(f"- 文本可读性优化: {'已启用' if args.improve_readability else '未启用'}")
        print(f"- 文本纠错: {'已启用，使用'+args.correction_model+'模型' if args.text_correction else '未启用'}")
        
        print("\n提示: 下次可以直接运行程序，然后输入BV号进行处理")
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())