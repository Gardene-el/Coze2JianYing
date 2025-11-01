"""
草稿生成器模块
从Coze输出完整转换到剪映草稿
结合 coze_parser + converter + material_manager + pyJianYingDraft
"""
from pathlib import Path
from typing import Optional, Dict, List, Any
import os
from utils.logger import get_logger
from utils.coze_parser import CozeOutputParser
from utils.converter import DraftInterfaceConverter
from utils.material_manager import MaterialManager, create_material_manager
from utils.draft_meta_manager import DraftMetaManager, create_draft_meta_manager
import pyJianYingDraft as draft
from pyJianYingDraft import ScriptFile  


class DraftGenerator:
    """剪映草稿生成器 - 从Coze输出到剪映草稿的完整转换"""
    
    # 默认剪映草稿路径
    DEFAULT_DRAFT_PATHS = [
        r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
        r"C:\Users\{username}\AppData\Roaming\JianyingPro\User Data\Projects\com.lveditor.draft",
    ]
    
    def __init__(self, output_base_dir: str = "./JianyingProjects"):
        """
        初始化草稿生成器
        
        Args:
            output_base_dir: 输出根目录(存放所有草稿项目)
        """
        self.logger = get_logger(__name__)
        self.logger.info("初始化草稿生成器")
        
        self.output_base_dir = output_base_dir
        self.parser = CozeOutputParser()
        self.material_managers: Dict[str, MaterialManager] = {}
        
        # 确保输出目录存在
        os.makedirs(output_base_dir, exist_ok=True)
        self.logger.info(f"输出目录: {output_base_dir}")
    
    def detect_default_draft_folder(self) -> Optional[str]:
        """
        自动检测剪映草稿文件夹
        
        Returns:
            检测到的文件夹路径，如果未检测到则返回None
        """
        username = os.getenv('USERNAME') or os.getenv('USER')
        
        for path_template in self.DEFAULT_DRAFT_PATHS:
            path = path_template.format(username=username)
            if os.path.exists(path) and os.path.isdir(path):
                self.logger.info(f"检测到剪映草稿文件夹: {path}")
                return path
        
        self.logger.warning("未能检测到剪映草稿文件夹")
        return None
    
    def generate(self, content: str, output_folder: Optional[str] = None) -> List[str]:
        """
        从Coze JSON内容生成剪映草稿
        
        Args:
            content: Coze输出的JSON字符串
            output_folder: 输出文件夹路径(可选,默认使用初始化时的路径)
            
        Returns:
            生成的草稿文件路径列表
            
        Raises:
            Exception: 草稿生成过程中的任何错误
        """
        self.logger.info(f"开始生成草稿，内容长度: {len(content)}")
        
        try:
            # 如果指定了output_folder，临时修改输出目录
            original_output_dir = self.output_base_dir
            if output_folder:
                self.output_base_dir = output_folder
                os.makedirs(output_folder, exist_ok=True)
                self.logger.info(f"使用指定输出文件夹: {output_folder}")
            
            # 1. 解析Coze输出
            self.logger.info("步骤1: 解析Coze输出...")
            self.parser.parse_from_clipboard(content)
            self.parser.print_summary()
            
            # 2. 获取标准化数据
            self.logger.info("步骤2: 标准化数据结构...")
            normalized_data = self.parser.get_normalized_data()
            self.logger.info("✅ 数据标准化完成")
            
            # 3. 转换所有草稿
            draft_paths = self._convert_drafts(normalized_data)
            
            # 恢复原始输出目录
            self.output_base_dir = original_output_dir
            
            self.logger.info(f"草稿生成完成，输出到: {draft_paths}")
            return draft_paths
            
        except Exception as e:
            self.logger.error(f"生成草稿时出错: {e}", exc_info=True)
            raise
    
    def generate_from_file(self, file_path: str, output_folder: Optional[str] = None) -> List[str]:
        """
        从Coze JSON文件生成剪映草稿
        
        Args:
            file_path: Coze输出JSON文件路径
            output_folder: 输出文件夹路径(可选)
            
        Returns:
            生成的草稿文件路径列表
        """
        self.logger.info(f"从文件生成草稿: {file_path}")
        
        try:
            # 如果指定了output_folder，临时修改输出目录
            original_output_dir = self.output_base_dir
            if output_folder:
                self.output_base_dir = output_folder
                os.makedirs(output_folder, exist_ok=True)
            
            # 1. 解析Coze输出
            self.logger.info("步骤1: 解析Coze输出...")
            self.parser.parse_from_file(file_path)
            self.parser.print_summary()
            
            # 2. 获取标准化数据
            self.logger.info("步骤2: 标准化数据结构...")
            normalized_data = self.parser.get_normalized_data()
            self.logger.info("✅ 数据标准化完成")
            
            # 3. 转换所有草稿
            draft_paths = self._convert_drafts(normalized_data)
            
            # 恢复原始输出目录
            self.output_base_dir = original_output_dir
            
            return draft_paths
            
        except Exception as e:
            self.logger.error(f"从文件生成草稿失败: {e}", exc_info=True)
            raise
    
    def _convert_drafts(self, parsed_data: Dict[str, Any]) -> List[str]:
        """
        转换所有草稿
        
        Args:
            parsed_data: 解析后的数据
            
        Returns:
            生成的草稿路径列表
        """
        draft_paths = []
        drafts = parsed_data.get('drafts', [])
        
        self.logger.info(f"步骤3: 开始转换 {len(drafts)} 个草稿...")
        
        for i, draft_data in enumerate(drafts, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"正在处理草稿 {i}/{len(drafts)}")
            self.logger.info(f"{'='*60}")
            
            try:
                draft_path = self._convert_single_draft(draft_data)
                draft_paths.append(draft_path)
                self.logger.info(f"✅ 草稿 {i} 生成成功: {draft_path}")
            except Exception as e:
                self.logger.error(f"❌ 草稿 {i} 生成失败: {e}")
                self.logger.exception("详细错误信息:")
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"转换完成! 成功: {len(draft_paths)}/{len(drafts)}")
        self.logger.info(f"{'='*60}")
        
        return draft_paths
    
    def _convert_single_draft(self, draft_data: Dict[str, Any]) -> str:
        """
        转换单个草稿
        
        Args:
            draft_data: 单个草稿数据
            
        Returns:
            草稿路径
        """
        # 1. 提取项目信息
        project = draft_data.get('project', {})
        draft_id = draft_data.get('draft_id', None)
        project_name = project.get('name', 'Coze剪映项目')
        width = project.get('width', 1920)
        height = project.get('height', 1080)
        fps = project.get('fps', 30)
        
        # 如果没有 draft_id，生成一个唯一 ID
        if not draft_id:
            import uuid
            draft_id = str(uuid.uuid4())
            self.logger.warning(f"未找到 draft_id，已生成: {draft_id}")
        
        # 组合文件夹名称：使用"扣子2剪映："前缀 + UUID
        # 这样既能避免剪映重命名（因为有人类可读前缀），又能保留UUID用于批量识别
        draft_folder_name = f"扣子2剪映：{draft_id}"
        
        self.logger.info(f"草稿ID: {draft_id}")
        self.logger.info(f"项目名称: {project_name}")
        self.logger.info(f"文件夹名称: {draft_folder_name}")
        self.logger.info(f"分辨率: {width}x{height}, 帧率: {fps}")
        
        # 2. 创建DraftFolder和Script
        # 重要: 使用"扣子2剪映：" + UUID 作为文件夹名
        # 这样可以避免剪映自动重命名文件夹（因为有人类可读前缀），同时保留UUID用于批量识别
        # 参考 pyJianYingDraft 的 demo.py，使用人类可读的名称不会被剪映重命名
        self.logger.info("创建草稿...")
        draft_folder_obj = draft.DraftFolder(self.output_base_dir)
        script: ScriptFile = draft_folder_obj.create_draft(
            draft_name=draft_folder_name,  # 使用"扣子2剪映：" + UUID 作为文件夹名
            width=width,
            height=height,
            fps=fps,
            allow_replace=True
        )
        
        # 草稿实际路径
        draft_folder = os.path.join(self.output_base_dir, draft_folder_name)
        
        # 3. 初始化MaterialManager
        # MaterialManager 现在将素材下载到 {draft_folder_path}/CozeJianYingAssistantAssets/{draft_folder_name}/
        self.logger.info("初始化MaterialManager...")
        material_manager = create_material_manager(
            draft_folder=draft_folder_obj,
            draft_name=draft_folder_name,  # 使用文件夹名称，与 create_draft 一致
            project_id=draft_id             # 传入 draft_id 用于素材文件夹命名
        )
        self.material_managers[draft_id] = material_manager  # 使用 draft_id 作为键
        
        # 4. 初始化Converter
        converter = DraftInterfaceConverter()
        
        # 5. 处理所有轨道
        tracks = draft_data.get('tracks', [])
        self.logger.info(f"处理 {len(tracks)} 条轨道...")
        
        for track_idx, track in enumerate(tracks, 1):
            track_type = track.get('track_type', 'unknown')
            segments = track.get('segments', [])
            self.logger.info(f"  轨道 {track_idx}: {track_type} ({len(segments)} 个片段)")
            
            # 6. 根据轨道类型创建对应的轨道
            track_name = f"{track_type}_track_{track_idx}"
            if not self._create_track_by_type(script, track_type, track_name):
                continue
            
            # 处理轨道中的所有片段
            for seg_idx, segment in enumerate(segments, 0):
                try:
                    self._process_segment(
                        segment=segment,
                        track_type=track_type,
                        track_name=track_name,
                        converter=converter,
                        material_manager=material_manager,
                        script=script,
                        seg_idx=seg_idx
                    )
                except Exception as e:
                    self.logger.error(f"    ❌ 片段 {seg_idx} 处理失败: {e}")
        
        # 7. 保存草稿
        self.logger.info("保存草稿...")
        script.save()
        
        # 8. 打印素材统计
        downloaded_materials = material_manager.list_downloaded_materials()
        self.logger.info(f"下载素材数量: {len(downloaded_materials)}")
        self.logger.info(f"素材文件夹大小: {material_manager.get_assets_folder_size():.2f} MB")
        
        return draft_folder
    
    def _create_track_by_type(self, script: ScriptFile, track_type: str, track_name: str) -> bool:
        """
        根据轨道类型创建对应的轨道
        
        Args:
            script: Script对象
            track_type: 轨道类型 ('audio', 'image', 'text', 'video')
            track_name: 轨道名称
            
        Returns:
            是否创建成功
        """
        try:
            if track_type == 'audio':
                script.add_track(draft.TrackType.audio, track_name)
                self.logger.info(f"  ✅ 创建音频轨道: {track_name}")
                return True
            elif track_type == 'image':
                # 图片轨道作为视频轨道处理
                script.add_track(draft.TrackType.video, track_name)
                self.logger.info(f"  ✅ 创建图片轨道(视频类型): {track_name}")
                return True
            elif track_type == 'text':
                script.add_track(draft.TrackType.text, track_name)
                self.logger.info(f"  ✅ 创建文本轨道: {track_name}")
                return True
            elif track_type == 'video':
                script.add_track(draft.TrackType.video, track_name)
                self.logger.info(f"  ✅ 创建视频轨道: {track_name}")
                return True
            else:
                self.logger.warning(f"  ⚠️  未知轨道类型: {track_type}，跳过轨道创建")
                return False
        except Exception as e:
            self.logger.error(f"  ❌ 创建轨道失败: {e}")
            return False
    
    def generate_root_meta_info(self, folder_path: Optional[str] = None):
        """
        生成 root_meta_info.json 文件
        扫描指定文件夹中的所有草稿并生成元信息文件
        
        Args:
            folder_path: 草稿文件夹路径（可选，默认使用 output_base_dir）
        """
        try:
            # 确定要扫描的文件夹
            target_folder = folder_path if folder_path else self.output_base_dir
            
            self.logger.info(f"开始生成 root_meta_info.json...")
            self.logger.info(f"目标文件夹: {target_folder}")
            
            # 创建元信息管理器
            meta_manager = create_draft_meta_manager()
            
            # 扫描草稿文件夹并生成元信息
            root_meta_info = meta_manager.scan_and_generate_meta_info(target_folder)
            
            # 保存到输出文件夹
            meta_info_path = os.path.join(target_folder, "root_meta_info.json")
            meta_manager.save_root_meta_info(root_meta_info, meta_info_path)
            
            self.logger.info("✅ root_meta_info.json 生成完成")
            return meta_info_path
            
        except Exception as e:
            self.logger.error(f"生成 root_meta_info.json 失败: {e}")
            raise
    
    def _process_segment(
        self,
        segment: Dict[str, Any],
        track_type: str,
        track_name: str,
        converter: DraftInterfaceConverter,
        material_manager: MaterialManager,
        script: ScriptFile,
        seg_idx: int
    ):
        """
        处理单个片段
        
        Args:
            segment: 片段数据
            track_type: 轨道类型
            track_name: 轨道名称
            converter: 转换器实例
            material_manager: 素材管理器实例
            script: Script对象
            seg_idx: 片段索引(用于日志)
        """
        segment_type = segment.get('type', track_type)
        
        # 下载素材(如果有material_url)
        material_url = segment.get('material_url')
        material_path = None  # 局部变量：素材的本地文件路径（仅用于image类型）
        
        if material_url:
            try:
                self.logger.info(f"    下载素材 {seg_idx}...")
                material = material_manager.create_material(material_url)
                segment['_material_object'] = material
                
                # 对于图片类型，额外保存本地文件路径到 material_path
                if segment_type == 'image':
                    material_path = material.path if hasattr(material, 'path') else None
                
                self.logger.info(f"    ✅ 素材下载成功")
            except Exception as e:
                self.logger.error(f"    ❌ 素材下载失败: {e}")
                return
        
        # 根据类型转换片段并添加到Script
        # 注意: pyJianYingDraft 的正确 API 是:
        #   1. script.add_track(TrackType, track_name) - 创建轨道
        #   2. script.add_segment(segment, track_name) - 添加片段到轨道
        try:
            material_obj = segment.get('_material_object')
            
            if segment_type == 'video' and material_obj:
                video_segment = converter.convert_video_segment_config(
                    segment_config=segment,
                    video_material=material_obj
                )
                script.add_segment(video_segment, track_name)
                self.logger.info(f"    ✅ 视频片段 {seg_idx} 添加到轨道 {track_name}")
                
            elif segment_type == 'audio' and material_obj:
                audio_segment = converter.convert_audio_segment_config(
                    segment_config=segment,
                    audio_material=material_obj
                )
                script.add_segment(audio_segment, track_name)
                self.logger.info(f"    ✅ 音频片段 {seg_idx} 添加到轨道 {track_name}")
                
            elif segment_type == 'image' and material_path:
                # 图片片段：直接使用本地文件路径 material_path
                video_segment = converter.convert_image_segment_config(
                    segment_config=segment,
                    image_file_path=material_path
                )
                script.add_segment(video_segment, track_name)
                self.logger.info(f"    ✅ 图片片段 {seg_idx} 添加到轨道 {track_name}")
                
            elif segment_type == 'text':
                self.logger.info(f"    转换文本片段...")
                text_segment = converter.convert_text_segment_config(segment)
                self.logger.info(f"    文本片段创建完成，类型: {type(text_segment)}")
                self.logger.info(f"    添加到轨道 {track_name}...")
                script.add_segment(text_segment, track_name)
                self.logger.info(f"    ✅ 文字片段 {seg_idx} 添加到轨道 {track_name}")
                
            else:
                self.logger.warning(f"    ⚠️  未知片段类型或缺少素材: {segment_type}")
                
        except Exception as e:
            self.logger.error(f"    ❌ 片段转换/添加失败: {e}")
            self.logger.error(f"       错误类型: {type(e).__name__}")
            self.logger.error(f"       错误repr: {repr(e)}")
            import traceback
            self.logger.error(f"       堆栈:\n{traceback.format_exc()}")
            # 不再重新抛出，避免中断整个轨道的处理
    
    def validate_content(self, content: str) -> bool:
        """
        验证内容是否有效
        
        Args:
            content: 待验证的内容
            
        Returns:
            是否有效
        """
        if not content or len(content.strip()) == 0:
            self.logger.warning("内容为空")
            return False
        
        # 尝试解析JSON
        try:
            import json
            json.loads(content)
            return True
        except json.JSONDecodeError:
            self.logger.warning("内容不是有效的JSON格式")
            return False
