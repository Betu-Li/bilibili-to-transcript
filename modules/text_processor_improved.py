import re
import jieba
import jieba.posseg as pseg

class TextProcessor:
    """文本后处理器，用于改善语音识别结果的可读性"""
    
    def __init__(self):
        # 加载结巴分词词典
        jieba.initialize()
        # 添加自定义词典
        self._add_custom_dict()
    
    def _add_custom_dict(self):
        """添加自定义词典，提高分词准确性"""
        # 添加常见的专有名词
        custom_words = [
            "江户川乱步", "人间椅子", "梅洛庞蒂", "知觉现象学",
            "短篇小说", "推理小说", "哲学", "文学史"
        ]
        for word in custom_words:
            jieba.add_word(word)
    
    def process(self, text):
        """处理文本，提高可读性
        
        Args:
            text: 原始文本
            
        Returns:
            str: 处理后的文本
        """
        # 检查输入文本是否为 None
        if text is None:
            print("警告: 输入到 process 的文本为 None，将返回空字符串。")
            return ""
            
        # 1. 预处理：去除多余空格，修正常见错误
        text = self._preprocess(text)
        
        # 2. 分词和词性标注
        words_with_pos = pseg.cut(text)
        
        # 3. 添加标点符号
        punctuated_text = self._add_punctuation(words_with_pos)
        
        # 4. 分段落
        paragraphed_text = self._split_paragraphs(punctuated_text)
        
        return paragraphed_text
    
    def _preprocess(self, text):
        """预处理文本"""
        # 修正常见错误
        text = self.correct_common_errors(text)
        
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _add_punctuation(self, words_with_pos):
        """根据词性添加标点符号"""
        result = []
        sentence = []
        word_count = 0
        last_pos = None
        
        for word, pos in words_with_pos:
            word = word.strip()
            if not word:  # 跳过空字符
                continue
                
            # 如果当前词已经有标点符号，直接添加
            if word in ['，', '。', '！', '？', '；', '：', ',', '.', '!', '?', ';', ':']:
                if sentence:
                    sentence[-1] = sentence[-1] + word
                continue
                
            sentence.append(word)
            word_count += 1
            
            # 在特定词性后添加逗号
            if pos in ['v', 'vn'] and word_count > 3 and last_pos not in ['wp', 'w']:
                if sentence and not sentence[-1][-1] in ['，', '。', '！', '？', '；', '：', ',', '.', '!', '?', ';', ':']:
                    sentence[-1] = sentence[-1] + '，'
                    word_count = 0
            
            # 在连词后添加逗号
            elif pos == 'c' and len(word) > 1:
                if sentence and not sentence[-1][-1] in ['，', '。', '！', '？', '；', '：', ',', '.', '!', '?', ';', ':']:
                    sentence[-1] = sentence[-1] + '，'
                    word_count = 0
            
            # 句子结束条件
            elif ((pos in ['wp', 'w']) or  # 标点符号
                 (pos in ['n', 'ns', 'nt', 'nz'] and word_count > 8) or  # 名词后且句子较长
                 (word_count >= 12)):  # 句子过长
                
                if sentence and not sentence[-1][-1] in ['，', '。', '！', '？', '；', '：', ',', '.', '!', '?', ';', ':']:
                    sentence[-1] = sentence[-1] + '。'
                    word_count = 0
            
            last_pos = pos
        
        # 合并句子
        text = ''.join(sentence)
        
        # 确保文本以句号结尾
        if text and text[-1] not in ['。', '！', '？', '.', '!', '?']:
            text += '。'
            
        return text
    
    def _split_paragraphs(self, text):
        """将文本分成段落"""
        # 按句号、感叹号、问号分割
        sentences = re.split(r'([。！？.!?])', text)
        
        # 重新组合句子，保留分隔符
        sentences = [''.join(i) for i in zip(sentences[0::2], sentences[1::2] + ['']) if i[0].strip()]
        
        paragraphs = []
        current_para = []
        sentence_count = 0
        char_count = 0
        
        for sentence in sentences:
            current_para.append(sentence)
            sentence_count += 1
            char_count += len(sentence)
            
            # 段落结束条件：句子数量达到阈值或字符数量达到阈值
            if (sentence_count >= 4) or (char_count >= 150):
                paragraphs.append(''.join(current_para))
                current_para = []
                sentence_count = 0
                char_count = 0
        
        # 添加最后一个段落
        if current_para:
            paragraphs.append(''.join(current_para))
        
        # 用换行符连接段落
        return '\n\n'.join(paragraphs)
    
    def correct_common_errors(self, text):
        """修正常见的语音识别错误"""
        # 检查输入文本是否为 None
        if text is None:
            print("警告: 输入到 correct_common_errors 的文本为 None，将返回空字符串。")
            return ""
            
        # 常见错误词典
        corrections = {
            # 示例：错误词: 正确词
            '江山烂布': '江户川乱步',
            '人间一着': '人间椅子',
            '人间一': '人间椅子',
            '一将': '匠人',
            '以降': '匠人',
            '架子': '家子',
            '夹子': '家子',
            '姨子': '椅子',
            '戒指': '介质',
            '税种': '这种',
            '一 ': '',  # 删除单独的"一",
            '一一': '',
            '一 一': '',
            '一 分 一': '',
            '一队': '一对',
            '一讲': '一样',
            '一顿': '一定',
            '驾驶着做': '假如这作',
            '头韩': '投函',
            '文件的': '闻到',
            '围歼': '围绕',
            '田地': '天地',
            '一王': '一室',
            '革新者': '客信者',
            '残害': '残骸',
            '自备': '自卑'
        }
        
        # 应用纠正
        for wrong, correct in corrections.items():
            # 再次检查 text 是否在循环中变为 None (虽然理论上不应该)
            if text is None:
                print("警告: 文本在 correct_common_errors 循环中变为 None，已中断处理。")
                return ""
            text = text.replace(wrong, correct)
        
        return text