"""
素材管理器
负责下载网络素材到草稿的Assets文件夹，并创建对应的Material对象
"""
from pathlib import Path
from typing import Union, Optional, Dict, Any
import pyJianYingDraft as draft
from src.backend.utils.logger import logger
from src.backend.utils.download import download as _download, _detect_content_type, _build_filename


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
        self.logger = logger
        
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
        # 不强制重新下载时，预测文件名并检查是否已存在
        if not force_download:
            content_type = _detect_content_type(url)
            target_filename = _build_filename(url=url, filename=filename, content_type=content_type)
            target_path = self.assets_path / target_filename
            if target_path.exists():
                self.logger.info(f"素材已存在，跳过下载: {target_filename}")
                return str(target_path)

        self.logger.info(f"开始下载素材: {url}")
        local_path = _download(url, str(self.assets_path), filename=filename)

        # 根据实际文件内容修正扩展名（如文件头与扩展名不符）
        file_path = Path(local_path)
        correct_filename = self._fix_filename_by_content(file_path, file_path.name)
        if correct_filename != file_path.name:
            self.logger.info(f"根据文件内容修正扩展名: {file_path.name} -> {correct_filename}")
            correct_path = file_path.parent / correct_filename
            file_path.rename(correct_path)
            local_path = str(correct_path)

        self.logger.info(
            f"✅ 素材下载完成: {Path(local_path).name} "
            f"({Path(local_path).stat().st_size / 1024 / 1024:.2f} MB)"
        )
        return local_path
    
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

