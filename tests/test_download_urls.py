#!/usr/bin/env python3
"""
测试脚本：使用 Coze2JianYing 项目的下载方案测试 GitHub Pages 资源下载

测试URL:
- https://gardene-el.github.io/Coze2JianYing/assets/sticker.gif
- https://gardene-el.github.io/Coze2JianYing/assets/video.mp4
- https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3
- https://gardene-el.github.io/Coze2JianYing/assets/subtitles.srt
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.backend.services.material import MaterialService
from app.backend.utils.logger import setup_logger, get_logger

def main():
    """主测试函数"""
    # 初始化日志
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)  # 确保日志目录存在
    log_file = log_dir / "test_download.log"
    setup_logger(log_file)
    logger = get_logger(__name__)
    
    logger.info("=" * 80)
    logger.info("开始测试 GitHub Pages 资源下载")
    logger.info("=" * 80)
    
    # 测试URL列表
    test_urls = [
        "https://gardene-el.github.io/Coze2JianYing/assets/sticker.gif",
        "https://gardene-el.github.io/Coze2JianYing/assets/video.mp4",
        "https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3",
        "https://gardene-el.github.io/Coze2JianYing/assets/subtitles.srt",
    ]
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix="coze2jy_download_test_")
    logger.info(f"创建临时测试目录: {test_dir}")
    
    try:
        # 初始化 MaterialService
        # 使用临时目录作为草稿根目录
        draft_folder_path = test_dir
        draft_name = "test_draft"
        project_id = "test_project_id"
        
        logger.info(f"初始化 MaterialService:")
        logger.info(f"  - draft_folder_path: {draft_folder_path}")
        logger.info(f"  - draft_name: {draft_name}")
        logger.info(f"  - project_id: {project_id}")
        
        manager = MaterialService(
            draft_folder_path=draft_folder_path,
            draft_name=draft_name,
            project_id=project_id
        )
        
        logger.info(f"Assets 目录路径: {manager.assets_path}")
        logger.info("")
        
        # 测试结果统计
        results = {
            "success": [],
            "failed": []
        }
        
        # 逐个测试URL
        for i, url in enumerate(test_urls, 1):
            logger.info("-" * 80)
            logger.info(f"测试 [{i}/{len(test_urls)}]: {url}")
            logger.info("-" * 80)
            
            try:
                # 尝试下载
                local_path = manager.download_material(url)
                
                # 检查文件是否存在
                if os.path.exists(local_path):
                    file_size = os.path.getsize(local_path)
                    logger.info(f"✅ 下载成功!")
                    logger.info(f"   本地路径: {local_path}")
                    logger.info(f"   文件大小: {file_size / 1024:.2f} KB")
                    
                    # 尝试检测素材类型
                    try:
                        material_type = manager._detect_material_type(Path(local_path))
                        logger.info(f"   检测类型: {material_type}")
                    except Exception as e:
                        logger.warning(f"   类型检测失败: {e}")
                    
                    results["success"].append({
                        "url": url,
                        "local_path": local_path,
                        "size": file_size
                    })
                else:
                    logger.error(f"❌ 下载失败: 文件不存在")
                    results["failed"].append({
                        "url": url,
                        "error": "文件不存在"
                    })
                    
            except Exception as e:
                logger.error(f"❌ 下载失败: {str(e)}")
                results["failed"].append({
                    "url": url,
                    "error": str(e)
                })
            
            logger.info("")
        
        # 打印测试总结
        logger.info("=" * 80)
        logger.info("测试总结")
        logger.info("=" * 80)
        logger.info(f"总计测试: {len(test_urls)} 个URL")
        logger.info(f"成功: {len(results['success'])} 个")
        logger.info(f"失败: {len(results['failed'])} 个")
        logger.info("")
        
        if results["success"]:
            logger.info("成功下载的文件:")
            for item in results["success"]:
                logger.info(f"  ✅ {item['url']}")
                logger.info(f"     路径: {item['local_path']}")
                logger.info(f"     大小: {item['size'] / 1024:.2f} KB")
        
        if results["failed"]:
            logger.info("")
            logger.info("下载失败的文件:")
            for item in results["failed"]:
                logger.error(f"  ❌ {item['url']}")
                logger.error(f"     错误: {item['error']}")
        
        # 显示 Assets 目录大小
        logger.info("")
        logger.info(f"Assets 目录总大小: {manager.get_assets_folder_size():.2f} MB")
        
        # 列出所有下载的文件
        logger.info("")
        logger.info("已下载的文件列表:")
        for filename in manager.list_downloaded_materials():
            logger.info(f"  - {filename}")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"测试完成! 临时文件保存在: {test_dir}")
        logger.info("=" * 80)
        
        # 返回结果
        return len(results["failed"]) == 0
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}", exc_info=True)
        return False
    
    finally:
        # 询问是否删除临时目录
        print("\n" + "=" * 80)
        print(f"临时测试目录: {test_dir}")
        print("=" * 80)
        user_input = input("是否删除临时测试目录? (y/n, 默认 n): ").strip().lower()
        
        if user_input == 'y':
            try:
                shutil.rmtree(test_dir)
                logger.info(f"已删除临时测试目录: {test_dir}")
                print(f"✅ 已删除临时测试目录")
            except Exception as e:
                logger.error(f"删除临时目录失败: {e}")
                print(f"❌ 删除临时目录失败: {e}")
        else:
            logger.info(f"保留临时测试目录: {test_dir}")
            print(f"📁 临时测试目录已保留，可手动查看下载的文件")


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
