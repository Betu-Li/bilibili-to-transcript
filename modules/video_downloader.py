import os
import subprocess
import re
import sys
from urllib.parse import urlparse

class VideoDownloader:
    def __init__(self, output_dir, cookies_path=None):
        self.output_dir = output_dir
        self.cookies_path = cookies_path
        os.makedirs(output_dir, exist_ok=True)
    
    def download(self, url):
        """
        下载B站视频
        
        Args:
            url: B站视频链接
            
        Returns:
            str: 下载的视频文件路径
        """
        # 验证URL格式
        if not self._validate_bilibili_url(url):
            raise ValueError("无效的B站视频链接")
        
        # 提取视频ID用于文件命名
        video_id = self._extract_video_id(url)
        output_path = os.path.join(self.output_dir, f"{video_id}.mp4")
        
        # 构建下载策略列表
        download_strategies = []
        
        # 基础命令
        base_command = ["you-get", "-o", self.output_dir, "-O", video_id]
        
        # 如果有cookies，添加cookies选项
        if self.cookies_path and os.path.exists(self.cookies_path):
            cookies_command = base_command + ["--cookies", self.cookies_path, url]
            download_strategies.append({
                "description": "使用cookies下载",
                "command": cookies_command
            })
        
        # 添加其他策略
        download_strategies.extend([
            # 策略1: 不指定格式，让you-get自动选择最合适的格式
            {
                "description": "自动选择最佳格式",
                "command": base_command + [url]
            },
            # 策略2: 指定低清晰度格式
            {
                "description": "指定低清晰度格式(360p)",
                "command": base_command + ["--format=dash-flv360", url]
            },
            # 策略3: 使用最低清晰度
            {
                "description": "使用最低清晰度",
                "command": base_command + ["--format=dash-flv", url]
            },
            # 策略4: 使用--no-proxy选项
            {
                "description": "使用无代理模式",
                "command": base_command + ["--no-proxy", url]
            }
        ])
        
        last_error = None
        for strategy in download_strategies:
            try:
                # 使用当前策略下载视频
                print(f"正在尝试下载策略: {strategy['description']}")
                subprocess.run(strategy["command"], check=True)
                
                # 检查文件是否存在
                if not os.path.exists(output_path):
                    # 尝试查找其他可能的文件名
                    for file in os.listdir(self.output_dir):
                        if file.startswith(video_id) and file.endswith(('.mp4', '.flv', '.webm')):
                            output_path = os.path.join(self.output_dir, file)
                            break
                
                if os.path.exists(output_path):
                    print(f"视频下载完成: {output_path}")
                    return output_path
                    
            except subprocess.CalledProcessError as e:
                print(f"下载策略 '{strategy['description']}' 失败: {e}")
                last_error = e
                continue  # 尝试下一个策略
        
        # 如果所有策略都失败，提供更详细的错误信息和解决方案
        print("\n===== 下载失败 =====")
        print("所有下载策略均失败，可能的原因:")
        print("1. 需要登录cookies (B站需要登录才能下载720p以上视频)")
        print("2. 网络连接问题")
        print("3. 视频可能需要大会员权限")
        print("\n解决方案:")
        print("1. 提供cookies文件: 使用浏览器登录B站后导出cookies，然后使用 --cookies 参数")
        print("   例如: python main.py --cookies=cookies.txt 视频链接")
        print("2. 手动下载视频并放置在输出目录中: " + self.output_dir)
        print("3. 检查网络连接或使用代理")
        
        if last_error:
            raise last_error
    
    def _validate_bilibili_url(self, url):
        """验证是否为有效的B站URL"""
        parsed = urlparse(url)
        return parsed.netloc in ["www.bilibili.com", "bilibili.com"]
    
    def _extract_video_id(self, url):
        """从URL中提取视频ID"""
        # 提取BV号
        bv_match = re.search(r'BV\w+', url)
        if bv_match:
            return bv_match.group(0)
        
        # 提取av号
        av_match = re.search(r'av(\d+)', url)
        if av_match:
            return f"av{av_match.group(1)}"
        
        # 如果都没有，使用URL的最后部分
        path = urlparse(url).path
        return path.split('/')[-1]