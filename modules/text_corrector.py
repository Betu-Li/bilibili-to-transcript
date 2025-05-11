import pycorrector

class TextCorrector:
    def __init__(self, model_name='macbert'):
        """
        初始化文本纠错器
        
        Args:
            model_name (str): 使用的模型名称。默认为 'macbert'，推荐的模型 <mcreference link="https://github.com/shibing624/pycorrector?tab=readme-ov-file#usage" index="0">0</mcreference>。
                                其他可选模型请参考 pycorrector 文档 <mcreference link="https://github.com/shibing624/pycorrector?tab=readme-ov-file#usage" index="0">0</mcreference>。
        """
        print(f"正在加载 pycorrector 模型: {model_name}...")
        # 根据选择的模型初始化，这里以默认的纠错方式为例
        # pycorrector 会自动下载所需的模型文件
        # 如果需要指定模型路径或使用其他模型，请参考 pycorrector 文档进行修改
        # 根据模型选择初始化对应的纠错器
        if model_name == 'macbert':
            from pycorrector import MacBertCorrector
            self.corrector = MacBertCorrector()
        else:
            # 默认或不支持的模型，可以考虑使用 KenlmCorrector 或抛出异常
            # 这里以 KenlmCorrector 为例，需要先 import
            from pycorrector import KenlmCorrector
            print(f"模型 '{model_name}' 不支持或未指定，将使用 KenlmCorrector。")
            self.corrector = KenlmCorrector()
        
        print("pycorrector 模型加载完成。")

    def correct(self, text):
        """
        对输入的文本进行纠错
        
        Args:
            text (str): 需要纠错的文本
            
        Returns:
            str: 纠错后的文本
        """
        print("正在进行文本纠错...")
        if isinstance(self.corrector, pycorrector.MacBertCorrector):
            corrected_sent, details = self.corrector.correct(text, max_length=128)
            
            if details:
                for error in details:
                    print(f"发现错误：{error['wrong']} → {error['correct']}，位置：{error['start']}-{error['end']}")
        else:
            # 对其他类型的 corrector 调用其 correct 方法
            # 注意：不同的 corrector 可能返回不同格式的结果，这里假设返回 (corrected_sent, detail)
            # KenlmCorrector 的 correct 方法只返回 corrected_sent
            if isinstance(self.corrector, pycorrector.KenlmCorrector):
                 corrected_sent = self.corrector.correct(text)
                 details = [] # Kenlm 没有详细的错误信息
            else:
                 # 对于未知的 corrector 类型，尝试调用，但可能出错
                 try:
                     corrected_sent, details = self.corrector.correct(text)
                 except TypeError: # 处理返回值数量不匹配等问题
                     corrected_sent = self.corrector.correct(text)
                     details = []
                 except Exception as e:
                     print(f"调用 {type(self.corrector).__name__}.correct 时出错: {e}")
                     corrected_sent = text # 出错时返回原文
                     details = []

        print("文本纠错完成。")
        if details:
             print(f"纠错详情: {details}")
        else:
             print("无详细纠错信息。")
        return corrected_sent

# 示例用法 (可以放在 main.py 或其他主流程文件中)
if __name__ == '__main__':
    corrector = TextCorrector()
    
    # 示例错误文本
    error_sentence = "这几话给我看蒙了，怎么个事请" 
    
    corrected_sentence = corrector.correct(error_sentence)
    
    print(f"原始文本: {error_sentence}")
    print(f"纠错后文本: {corrected_sentence}")

    error_sentence_2 = "机器学习是人工智能领遇的一个重要分知"
    corrected_sentence_2 = corrector.correct(error_sentence_2)
    print(f"原始文本: {error_sentence_2}")
    print(f"纠错后文本: {corrected_sentence_2}")