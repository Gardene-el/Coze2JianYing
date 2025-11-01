"""
素材管理器
负责下载网络素材到草稿的Assets文件夹，并创建对应的Material对象
"""
import os
import requests
import hashlib
from pathlib import Path
from typing import Union, Optional, Dict, Any
from urllib.parse import urlparse, unquote
import pyJianYingDraft as draft
from utils.logger import get_logger


class MaterialManager:
    """
    素材下载和管理器
    
    功能:
    1. 从URL下载素材到草稿的Assets文件夹
    2. 自动识别素材类型(视频/音频/图片)
    3. 创建对应的Material对象
    4. 支持素材缓存(避免重复下载)
    """
    
    def __init__(self, draft_folder_path: str, draft_name: str, project_id: Optional[str] = None):
        """
        初始化素材管理器
        
        Args:
            draft_folder_path: 草稿根文件夹路径 (DraftFolder的folder_path)
                例: "C:/Users/你的用户名/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft"
            draft_name: 具体草稿名称
                例: "我的项目"
            project_id: 项目ID (可选，用于素材文件夹命名)
                例: "68c1a119-02b9-401f-9bac-fda50e86727d"
                
        最终Assets路径: {draft_folder_path}/CozeJianYingAssistantAssets/{project_id}/
        如果未提供project_id，则使用旧路径: {draft_folder_path}/{draft_name}/Assets/
        """
        self.logger = get_logger(__name__)
        
        # 草稿路径
        self.draft_folder_path = Path(draft_folder_path)
        self.draft_name = draft_name
        self.draft_path = self.draft_folder_path / draft_name
        self.project_id = project_id or draft_name  # 如果没有提供project_id，使用draft_name
        
        # Assets文件夹路径 - 新逻辑：在草稿根目录下的CozeJianYingAssistantAssets文件夹中
        if project_id:
            # 新路径: {draft_folder_path}/CozeJianYingAssistantAssets/{project_id}/
            self.assets_base_path = self.draft_folder_path / "CozeJianYingAssistantAssets"
            self.assets_path = self.assets_base_path / project_id
        else:
            # 旧路径（兼容性）: {draft_folder_path}/{draft_name}/Assets/
            self.assets_path = self.draft_path / "Assets"
        
        # 素材缓存 {url: material_object}
        self.material_cache: Dict[str, Union[draft.VideoMaterial, draft.AudioMaterial]] = {}
        
        # 确保Assets文件夹存在
        self._ensure_assets_folder()
        
        self.logger.info(f"素材管理器已初始化: {self.assets_path}")
    
    def _ensure_assets_folder(self) -> None:
        """确保Assets文件夹存在"""
        if not self.assets_path.exists():
            self.assets_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"创建Assets文件夹: {self.assets_path}")
        else:
            self.logger.debug(f"Assets文件夹已存在: {self.assets_path}")
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """
        根据Content-Type获取文件扩展名
        
        Args:
            content_type: HTTP Content-Type header值
            
        Returns:
            文件扩展名 (带点，如 '.jpg')
        """
        # Content-Type 映射表
        mime_to_ext = {
            # 图片
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/bmp': '.bmp',
            'image/svg+xml': '.svg',
            # 视频
            'video/mp4': '.mp4',
            'video/quicktime': '.mov',
            'video/x-msvideo': '.avi',
            'video/x-matroska': '.mkv',
            'video/webm': '.webm',
            # 音频
            'audio/mpeg': '.mp3',
            'audio/mp3': '.mp3',
            'audio/wav': '.wav',
            'audio/wave': '.wav',
            'audio/x-wav': '.wav',
            'audio/aac': '.aac',
            'audio/ogg': '.ogg',
            'audio/flac': '.flac',
        }
        
        # 移除参数部分 (如 "image/jpeg; charset=utf-8")
        content_type = content_type.split(';')[0].strip().lower()
        
        return mime_to_ext.get(content_type, '.mp4')  # 默认 .mp4
    
    def _get_filename_from_url(self, url: str, content_type: Optional[str] = None) -> str:
        """
        从URL提取文件名
        
        Args:
            url: 素材URL
            content_type: HTTP Content-Type (可选，用于无扩展名URL)
            
        Returns:
            文件名
        """
        # 解析URL
        parsed = urlparse(url)
        
        # 尝试从路径获取文件名
        path = unquote(parsed.path)
        filename = os.path.basename(path)
        
        # 如果没有扩展名，使用Content-Type或生成唯一文件名
        if not filename or '.' not in filename:
            # 使用URL的MD5作为文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            
            # 尝试从Content-Type获取扩展名
            if content_type:
                ext = self._get_extension_from_content_type(content_type)
                filename = f"material_{url_hash}{ext}"
                self.logger.info(f"根据Content-Type ({content_type}) 生成文件名: {filename}")
            else:
                filename = f"material_{url_hash}.mp4"  # 默认为mp4
                self.logger.warning(f"无法从URL提取文件名，使用默认mp4: {filename}")
        
        return filename
    
    def _detect_material_type(self, file_path: Path) -> str:
        """
        根据文件扩展名和文件头检测素材类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            'video', 'audio', 或 'image'
        """
        ext = file_path.suffix.lower()
        
        # 首先根据扩展名进行基本判断
        # 视频格式
        video_exts = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm', '.m4v', '.mpg', '.mpeg'}
        if ext in video_exts:
            return 'video'
        
        # 音频格式
        audio_exts = {'.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a', '.wma', '.ape'}
        if ext in audio_exts:
            return 'audio'
        
        # 图片格式
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico'}
        if ext in image_exts:
            return 'image'
        
        # 如果扩展名不明确，尝试检查文件头（魔术数字）
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)  # 读取前16字节
            
            # 检查常见的文件头签名
            if header.startswith(b'\xFF\xD8\xFF'):  # JPEG
                self.logger.info(f"通过文件头检测到JPEG图片: {file_path.name}")
                return 'image'
            elif header.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                self.logger.info(f"通过文件头检测到PNG图片: {file_path.name}")
                return 'image'
            elif header.startswith(b'GIF8'):  # GIF
                self.logger.info(f"通过文件头检测到GIF图片: {file_path.name}")
                return 'image'
            elif header.startswith(b'RIFF') and b'WEBP' in header:  # WEBP
                self.logger.info(f"通过文件头检测到WEBP图片: {file_path.name}")
                return 'image'
            elif header.startswith((b'\x00\x00\x00\x14ftypmp4', b'\x00\x00\x00\x18ftypmp4', b'\x00\x00\x00\x20ftypmp4')):  # MP4
                self.logger.info(f"通过文件头检测到MP4视频: {file_path.name}")
                return 'video'
            elif header.startswith(b'ID3') or header.startswith(b'\xFF\xFB'):  # MP3
                self.logger.info(f"通过文件头检测到MP3音频: {file_path.name}")
                return 'audio'
            elif header.startswith(b'RIFF') and b'WAVE' in header:  # WAV
                self.logger.info(f"通过文件头检测到WAV音频: {file_path.name}")
                return 'audio'
                
        except Exception as e:
            self.logger.warning(f"无法读取文件头进行类型检测: {e}")
        
        # 如果都不匹配，检查文件是否可能是HTML错误页面
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content_start = f.read(200).lower()
                if '<html' in content_start or '<!doctype html' in content_start:
                    self.logger.error(f"检测到HTML内容，可能下载了错误页面: {file_path.name}")
                    raise ValueError(f"下载的文件是HTML页面而不是媒体文件: {file_path.name}")
        except UnicodeDecodeError:
            # 二进制文件，这是好的
            pass
        except ValueError as ve:
            # 重新抛出HTML错误
            if "HTML页面" in str(ve):
                raise
            # 其他ValueError继续处理
            self.logger.debug(f"HTML内容检查出现ValueError: {ve}")
        except Exception as e:
            self.logger.debug(f"HTML内容检查出现异常（可能是正常的二进制文件）: {e}")
        
        # 默认当作视频，但给出警告
        self.logger.warning(f"未识别的文件格式 {ext}，默认作为视频处理")
        return 'video'
    
    def _fix_filename_by_content(self, file_path: Path, original_filename: str) -> str:
        """
        根据文件实际内容修正文件名扩展名
        
        Args:
            file_path: 文件路径
            original_filename: 原始文件名
            
        Returns:
            修正后的文件名
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
            
            # 提取原始文件名（不含扩展名）
            name_without_ext = Path(original_filename).stem
            
            # 根据文件头确定正确的扩展名
            if header.startswith(b'\xFF\xD8\xFF'):  # JPEG
                return f"{name_without_ext}.jpg"
            elif header.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
                return f"{name_without_ext}.png"
            elif header.startswith(b'GIF8'):  # GIF
                return f"{name_without_ext}.gif"
            elif header.startswith(b'RIFF') and b'WEBP' in header:  # WEBP
                return f"{name_without_ext}.webp"
            elif header.startswith((b'\x00\x00\x00\x14ftypmp4', b'\x00\x00\x00\x18ftypmp4', b'\x00\x00\x00\x20ftypmp4')):  # MP4
                return f"{name_without_ext}.mp4"
            elif header.startswith(b'ID3') or header.startswith(b'\xFF\xFB'):  # MP3
                return f"{name_without_ext}.mp3"
            elif header.startswith(b'RIFF') and b'WAVE' in header:  # WAV
                return f"{name_without_ext}.wav"
            
        except Exception as e:
            self.logger.warning(f"无法检查文件内容来修正扩展名: {e}")
        
        # 如果无法确定，返回原始文件名
        return original_filename
    
    def download_material(
        self, 
        url: str, 
        filename: Optional[str] = None,
        force_download: bool = False
    ) -> str:
        """
        从URL下载素材到Assets文件夹
        
        Args:
            url: 素材的网络地址
            filename: 自定义文件名（可选）
            force_download: 是否强制重新下载（即使文件已存在）
            
        Returns:
            下载后的本地文件路径
            
        Raises:
            requests.RequestException: 下载失败
        """
        # 如果没有指定文件名,先发送HEAD请求获取Content-Type
        content_type = None
        if filename is None:
            try:
                # 增加更长的超时时间和更好的请求头
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                head_response = requests.head(url, timeout=30, allow_redirects=True, headers=headers)
                content_type = head_response.headers.get('Content-Type', None)
                self.logger.debug(f"检测到Content-Type: {content_type}")
            except Exception as e:
                self.logger.warning(f"HEAD请求失败,将使用默认扩展名: {e}")
        
        # 确定文件名
        if filename is None:
            filename = self._get_filename_from_url(url, content_type)
        
        # 目标路径
        target_path = self.assets_path / filename
        
        # 检查文件是否已存在
        if target_path.exists() and not force_download:
            self.logger.info(f"素材已存在，跳过下载: {filename}")
            return str(target_path)
        
        # 下载文件 - 添加重试机制
        self.logger.info(f"开始下载素材: {url}")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 更好的请求头和更长的超时时间
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'image/*,video/*,audio/*,*/*',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                response = requests.get(
                    url, 
                    stream=True, 
                    timeout=60,  # 增加到60秒超时
                    headers=headers,
                    allow_redirects=True
                )
                response.raise_for_status()
                
                # 检查响应的Content-Type是否合理
                actual_content_type = response.headers.get('Content-Type', '')
                self.logger.debug(f"实际Content-Type: {actual_content_type}")
                
                # 创建临时文件先写入
                temp_path = target_path.with_suffix(target_path.suffix + '.tmp')
                
                # 写入文件，增加进度监控
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded_size = 0
                
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # 每下载1MB打印一次进度（避免日志过多）
                            if downloaded_size % (1024 * 1024) == 0:
                                if total_size > 0:
                                    progress = (downloaded_size / total_size) * 100
                                    self.logger.debug(f"下载进度: {progress:.1f}% ({downloaded_size / 1024 / 1024:.1f}MB)")
                
                # 检查下载的文件大小是否合理
                if temp_path.stat().st_size < 100:  # 小于100字节可能是错误页面
                    self.logger.warning(f"下载的文件过小({temp_path.stat().st_size}字节)，可能是错误内容")
                    temp_path.unlink()  # 删除临时文件
                    if attempt < max_retries - 1:
                        self.logger.info(f"第{attempt + 1}次尝试失败，等待2秒后重试...")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        raise ValueError("下载的文件过小，可能是错误内容")
                
                # 检查实际文件内容并修正扩展名（如果需要）
                correct_filename = self._fix_filename_by_content(temp_path, filename)
                if correct_filename != filename:
                    self.logger.info(f"根据文件内容修正扩展名: {filename} -> {correct_filename}")
                    final_path = self.assets_path / correct_filename
                    temp_path.rename(final_path)
                else:
                    final_path = target_path
                    temp_path.rename(final_path)
                
                self.logger.info(f"✅ 素材下载完成: {final_path.name} ({final_path.stat().st_size / 1024 / 1024:.2f} MB)")
                return str(final_path)
                
            except requests.RequestException as e:
                self.logger.warning(f"第{attempt + 1}次下载尝试失败: {e}")
                if attempt < max_retries - 1:
                    self.logger.info(f"等待{(attempt + 1) * 2}秒后重试...")
                    import time
                    time.sleep((attempt + 1) * 2)  # 递增等待时间
                else:
                    self.logger.error(f"❌ 所有下载尝试均失败: {url}")
                    raise
            except Exception as e:
                self.logger.error(f"下载过程中发生未知错误: {e}")
                if attempt < max_retries - 1:
                    self.logger.info(f"等待{(attempt + 1) * 2}秒后重试...")
                    import time
                    time.sleep((attempt + 1) * 2)
                else:
                    raise
        
        # 如果所有重试都失败，这里不应该到达，但为了类型安全添加
        raise RuntimeError("下载失败：所有重试尝试均已用尽")
    
    def create_material(
        self,
        url: str,
        filename: Optional[str] = None,
        force_download: bool = False
    ) -> Union[draft.VideoMaterial, draft.AudioMaterial]:
        """
        从URL下载素材并创建对应的Material对象
        
        这是最常用的方法！
        
        Args:
            url: 素材的网络地址
            filename: 自定义文件名（可选）
            force_download: 是否强制重新下载
            
        Returns:
            VideoMaterial 或 AudioMaterial 对象
            
        Raises:
            requests.RequestException: 下载失败
            ValueError: 不支持的素材类型
        """
        # 检查缓存
        if url in self.material_cache and not force_download:
            self.logger.debug(f"从缓存获取素材: {url}")
            return self.material_cache[url]
        
        # 下载素材并通过本地路径创建Material对象
        local_path = self.download_material(url, filename, force_download)
        material = self.create_material_from_local_path(local_path, source_url=url)
        return material

    def create_material_from_local_path(
        self,
        local_path: str,
        source_url: Optional[str] = None
    ) -> Union[draft.VideoMaterial, draft.AudioMaterial]:
        """
        根据本地文件路径创建 Material 对象（不执行下载）。

        Args:
            local_path: 本地文件路径
            source_url: 可选的来源 URL，用于将创建的 material 缓存到 material_cache

        Returns:
            VideoMaterial 或 AudioMaterial 对象
        """
        file_path = Path(local_path)
        material_type = self._detect_material_type(file_path)

        if material_type == 'video':
            material = draft.VideoMaterial(str(file_path))
            self.logger.info(f"✅ 创建VideoMaterial: {file_path.name}")

        elif material_type == 'audio':
            material = draft.AudioMaterial(str(file_path))
            self.logger.info(f"✅ 创建AudioMaterial: {file_path.name}")

        elif material_type == 'image':
            # 图片作为VideoMaterial处理（pyJianYingDraft的设计）
            material = draft.VideoMaterial(str(file_path))
            self.logger.info(f"✅ 创建VideoMaterial (图片): {file_path.name}")

        else:
            raise ValueError(f"不支持的素材类型: {material_type}")

        # 如果提供了来源URL，则缓存该 material，便于后续按 URL 查找
        if source_url:
            self.material_cache[source_url] = material

        return material
    
    def create_video_material(
        self,
        url: str,
        filename: Optional[str] = None,
        force_download: bool = False
    ) -> draft.VideoMaterial:
        """
        创建视频素材（快捷方法）
        
        Args:
            url: 视频URL
            filename: 自定义文件名（可选）
            force_download: 是否强制重新下载
            
        Returns:
            VideoMaterial 对象
        """
        material = self.create_material(url, filename, force_download)
        if not isinstance(material, draft.VideoMaterial):
            raise ValueError(f"URL指向的不是视频素材: {url}")
        return material
    
    def create_audio_material(
        self,
        url: str,
        filename: Optional[str] = None,
        force_download: bool = False
    ) -> draft.AudioMaterial:
        """
        创建音频素材（快捷方法）
        
        Args:
            url: 音频URL
            filename: 自定义文件名（可选）
            force_download: 是否强制重新下载
            
        Returns:
            AudioMaterial 对象
        """
        material = self.create_material(url, filename, force_download)
        if not isinstance(material, draft.AudioMaterial):
            raise ValueError(f"URL指向的不是音频素材: {url}")
        return material
    
    def batch_create_materials(
        self,
        urls: list[str],
        force_download: bool = False
    ) -> Dict[str, Union[draft.VideoMaterial, draft.AudioMaterial]]:
        """
        批量下载并创建素材
        
        Args:
            urls: URL列表
            force_download: 是否强制重新下载
            
        Returns:
            {url: material} 映射字典
        """
        self.logger.info(f"开始批量下载 {len(urls)} 个素材")
        
        results = {}
        for i, url in enumerate(urls, 1):
            try:
                self.logger.info(f"处理 [{i}/{len(urls)}]: {url}")
                material = self.create_material(url, force_download=force_download)
                results[url] = material
            except Exception as e:
                self.logger.error(f"处理素材失败 [{i}/{len(urls)}]: {url} - {e}")
                continue
        
        self.logger.info(f"✅ 批量下载完成: {len(results)}/{len(urls)} 成功")
        return results
    
    def get_material_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        获取已下载素材的信息
        
        Args:
            url: 素材URL
            
        Returns:
            素材信息字典，如果未下载则返回None
        """
        if url not in self.material_cache:
            return None
        
        material = self.material_cache[url]
        
        info = {
            "url": url,
            "type": "video" if isinstance(material, draft.VideoMaterial) else "audio",
            "local_path": material.path if hasattr(material, 'path') else None,
            "cached": True
        }
        
        return info
    
    def clear_cache(self) -> None:
        """清除素材缓存（不删除文件）"""
        count = len(self.material_cache)
        self.material_cache.clear()
        self.logger.info(f"已清除 {count} 个素材缓存")
    
    def get_assets_folder_size(self) -> float:
        """
        获取Assets文件夹大小
        
        Returns:
            文件夹大小（MB）
        """
        total_size = 0
        for file in self.assets_path.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
        
        return total_size / 1024 / 1024  # 转换为MB
    
    def list_downloaded_materials(self) -> list[str]:
        """
        列出Assets文件夹中所有已下载的素材
        
        Returns:
            文件名列表
        """
        if not self.assets_path.exists():
            return []
        
        return [f.name for f in self.assets_path.iterdir() if f.is_file()]


# ========== 便捷函数 ==========

def create_material_manager(
    draft_folder: draft.DraftFolder,
    draft_name: str,
    project_id: Optional[str] = None
) -> MaterialManager:
    """
    便捷函数：从DraftFolder对象创建MaterialManager
    
    Args:
        draft_folder: DraftFolder对象
        draft_name: 草稿名称
        project_id: 项目ID (可选，用于素材文件夹命名)
        
    Returns:
        MaterialManager 实例
        
    Example:
        >>> draft_folder = draft.DraftFolder("C:/path/to/drafts")
        >>> manager = create_material_manager(draft_folder, "我的项目", "68c1a119-02b9-401f-9bac-fda50e86727d")
        >>> video_material = manager.create_video_material("https://example.com/video.mp4")
    """
    return MaterialManager(draft_folder.folder_path, draft_name, project_id)

