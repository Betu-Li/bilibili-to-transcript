import re
import jieba
import jieba.posseg as pseg

class TextProcessor:
    """文本后处理器，用于改善语音识别结果的可读性"""
    
    def __init__(self):
        # 加载结巴分词词典
        jieba.initialize()
    
    def process(self, text):
        """处理文本，提高可读性
        
        Args:
            text: 原始文本
            
        Returns:
            str: 处理后的文本
        """
        # 1. 分词和词性标注
        words_with_pos = pseg.cut(text)
        
        # 2. 添加标点符号
        punctuated_text = self._add_punctuation(words_with_pos)
        
        # 3. 分段落
        paragraphed_text = self._split_paragraphs(punctuated_text)
        
        return paragraphed_text
    
    def _add_punctuation(self, words_with_pos):
        """根据词性添加标点符号"""
        result = []
        sentence = []
        word_count = 0
        
        for word, pos in words_with_pos:
            word = word.strip()
            if not word:  # 跳过空字符
                continue
                
            sentence.append(word)
            word_count += 1
            
            # 在特定词性后添加标点
            if pos in ['v', 'vn'] and word_count > 5:  # 动词后可能是句子结束
                if len(sentence) > 0 and not sentence[-1][-1] in ['，', '。', '！', '？', '；', '：']:
                    sentence[-1] = sentence[-1] + '，'
                    word_count = 0
            
            # 句子结束条件
            if (pos in ['wp', 'w'] or  # 标点符号
                (pos in ['n', 'ns', 'nt', 'nz'] and word_count > 10) or  # 名词后且句子较长
                word_count >= 15):  # 句子过长
                
                if len(sentence) > 0 and not sentence[-1][-1] in ['，', '。', '！', '？', '；', '：']:
                    sentence[-1] = sentence[-1] + '。'
                    word_count = 0
        
        # 合并句子
        text = ''.join(sentence)
        
        # 确保文本以句号结尾
        if text and text[-1] not in ['。', '！', '？']:
            text += '。'
            
        return text
    
    def _split_paragraphs(self, text):
        """将文本分成段落"""
        # 按句号、感叹号、问号分割
        sentences = re.split(r'([。！？])', text)
        
        # 重新组合句子，保留分隔符
        sentences = [''.join(i) for i in zip(sentences[0::2], sentences[1::2] + ['']) if i[0].strip()]
        
        paragraphs = []
        current_para = []
        
        for sentence in sentences:
            current_para.append(sentence)
            
            # 每3-5个句子形成一个段落
            if len(current_para) >= 3 and (len(current_para) >= 5 or '。' in sentence):
                paragraphs.append(''.join(current_para))
                current_para = []
        
        # 添加最后一个段落
        if current_para:
            paragraphs.append(''.join(current_para))
        
        # 用两个换行符连接段落
        return '\n\n'.join(paragraphs)
    
    def correct_common_errors(self, text):
        """修正常见的语音识别错误"""
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
            # 可以根据实际情况添加更多
        }
        
        # 应用纠正
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
            
        return text


class TextProcessorBase:
    def process(self, text):
        raise NotImplementedError

class SnowNLPProcessor(TextProcessorBase):
    def __init__(self):
        from snownlp import SnowNLP
        
    def process(self, text):
        s = SnowNLP(text)
        return ' '.join([word for sentence in s.sentences for word in sentence])

class THULACProcessor(TextProcessorBase):
    def __init__(self):
        import thulac
        from config import ProcessorConfig
        self.thulac = thulac.thulac(model_path=ProcessorConfig.THULAC_MODEL_PATH)
        
    def process(self, text):
        return self.thulac.cut(text, text=True)

class HanLPProcessor(TextProcessorBase):
    def __init__(self):
        from pyhanlp import HanLP
        from config import ProcessorConfig
        HanLP.Config.enableDebug = ProcessorConfig.HANLP_CONFIG['enable_custom_dict']
        
    def process(self, text):
        return ' '.join([term.word for term in HanLP.segment(text)])


def get_processor():
    from config import TEXT_PROCESSOR
    
    processors = {
        'snownlp': SnowNLPProcessor,
        'thulac': THULACProcessor,
        'hanlp': HanLPProcessor,
        'jieba': TextProcessor
    }
    
    return processors[TEXT_PROCESSOR.lower()]()