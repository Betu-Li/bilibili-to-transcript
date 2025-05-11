# B站视频转文字稿程序配置文件

# 下载设置
DOWNLOAD_DIR = "./output/videos"
AUDIO_DIR = "./output/audio"
TRANSCRIPT_DIR = "./output/transcripts"

# 音频设置
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
SEGMENT_LENGTH_MS = 300000  # 5分钟切片

# 语音识别设置
# 选择识别引擎: "vosk" 或 "aliyun" 或 "tencent"
RECOGNITION_ENGINE = "vosk"

# Vosk模型设置
VOSK_MODEL_PATH = "vosk-model-cn-0.22" # 模型路径设置

# 云服务API设置 (如果使用)
ALIYUN_ACCESS_KEY = ""
ALIYUN_ACCESS_SECRET = ""
ALIYUN_APPKEY = ""

TENCENT_SECRET_ID = ""
TENCENT_SECRET_KEY = ""

# 文本纠错处理功能设置
TEXT_CORRECTION_ENABLED = True
TEXT_CORRECTION_MODEL = 'macbert'# 可选值：macbert

# 文本处理器设置
TEXT_PROCESSOR = "snownlp"  # 可选值：snownlp/thulac/hanlp/jieba

class ProcessorConfig:
    THULAC_MODEL_PATH = "./models/thulac_models"
    HANLP_CONFIG = {
        "enable_custom_dict": True
    }