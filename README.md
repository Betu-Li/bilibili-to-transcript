# Bilibili-to-Transcript

这是一个 Python 项目，旨在从 Bilibili 视频中提取音频并将其转换为文本字幕。

## 功能

*   **视频下载**: 从 Bilibili 下载视频。
*   **音频提取**: 从下载的视频中提取音频轨道。
*   **语音识别**: 将提取的音频转换为文本。
*   **文本后处理**: 对识别出的文本进行标点添加、分段和常见错误修正，以提高可读性。
*   **文本生成**: 将处理后的文本生成 `.srt` 和 `.txt` 格式的字幕文件。
*   **多种模型支持**: 支持 Vosk, MacBERT, KenLM 等多种语音识别和文本纠错模型。

## 项目结构

```
.bilibili-to-transcript/
├── .venv/                  # Python 虚拟环境
├── modules/                # 项目核心模块
│   ├── audio_extractor.py  # 音频提取
│   ├── speech_recognizer.py # 语音识别
│   ├── text_corrector.py   # 文本纠错
│   ├── text_processor.py   # 文本后处理
│   ├── transcript_generator.py # 字幕生成
│   └── video_downloader.py # 视频下载
├── output/                 # 输出目录
│   ├── audio/              # 提取的音频文件
│   ├── transcripts/        # 生成的字幕文件
│   └── videos/             # 下载的视频文件
├── vosk-model-cn-0.22/     # Vosk 中文模型
├── config.py               # 配置文件
├── main.py                 # 主程序入口
├── requirements.txt        # Python 依赖
└── README.md               # 项目说明
```

## 安装

1.  **克隆仓库**:
    ```bash
    git clone <your-repository-url>
    cd bilibili-to-transcript
    ```

2.  **创建并激活虚拟环境** (推荐):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    # .venv\Scripts\activate    # Windows
    ```

3.  **安装依赖**: 
    ```bash
    pip install -r requirements.txt
    ```

4.  **下载模型**:
    *   根据 `config.py` 中的配置，可能需要手动下载并放置相应的语音识别模型 (如 Vosk) 和文本纠错模型到指定路径。

## 使用方法

1.  **配置 `config.py`**:
    *   设置 `VIDEO_URLS` 为你想要处理的 Bilibili 视频链接列表。
    *   根据需要调整其他配置，如输出目录、使用的模型等。

2.  **运行主程序**:
    ```bash
    python main.py
    ```

3.  **查看输出**:
    *   处理完成的视频、音频和字幕文件将保存在 `output/` 目录下对应的子文件夹中。

## 配置项 (`config.py`)

主要的配置项包括：

*   `VIDEO_URLS`: Bilibili 视频链接列表。
*   `OUTPUT_PATH`: 输出文件的根目录。
*   `SPEECH_RECOGNIZER`: 选择语音识别器 (`vosk`, `whisper` 等)。
*   `TEXT_CORRECTOR_MODEL`: 选择文本纠错模型 (`macbert`, `kenlm` 等)。
*   `TEXT_PROCESSOR`: 选择文本后处理器 (`jieba`, `snownlp`, `thulac`, `hanlp`)。
*   模型路径配置 (如 `VOSK_MODEL_PATH`)。

请根据你的需求和环境修改这些配置。

## 如何贡献

欢迎为此项目贡献代码！你可以通过以下方式参与：

1.  Fork 本仓库。
2.  创建新的分支 (`git checkout -b feature/YourFeature`)。
3.  提交你的更改 (`git commit -am 'Add some feature'`)。
4.  将更改推送到分支 (`git push origin feature/YourFeature`)。
5.  创建一个新的 Pull Request。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。