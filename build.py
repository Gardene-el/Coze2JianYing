"""
打包脚本 - 使用PyInstaller将应用打包为exe
"""
import sys
import PyInstaller.__main__
import shutil
from pathlib import Path

# 设置 UTF-8 编码以支持中文输出
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python 3.6 及更早版本不支持 reconfigure
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)


def build_exe():
    """构建exe文件"""
    print("开始打包应用程序...")
    
    # 根据操作系统确定路径分隔符 (Windows: ';', Linux/Mac: ':')
    import os
    separator = ';' if os.name == 'nt' else ':'
    
    # 获取 pyJianYingDraft 的 assets 路径
    try:
        import pyJianYingDraft
        pyjy_path = Path(pyJianYingDraft.__file__).parent
        pyjy_assets = pyjy_path / 'assets'
        print(f"找到 pyJianYingDraft assets: {pyjy_assets}")
    except Exception as e:
        print(f"警告: 无法找到 pyJianYingDraft assets: {e}")
        pyjy_assets = None
    
    # PyInstaller参数
    args = [
        'app/main.py',              # 主程序入口
        '--name=CozeJianYingDraftGenerator',  # 应用名称
        '--windowed',                # 不显示控制台窗口
        '--onefile',                 # 打包成单个exe文件
        '--clean',                   # 清理临时文件
        # '--icon=resources/icon.ico', # 应用图标（如果有的话）
        f'--add-data=resources{separator}resources',  # 添加资源文件
        '--hidden-import=tkinter',   # 确保包含tkinter
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=pyJianYingDraft',  # 添加pyJianYingDraft库
        '--noconfirm',               # 不询问确认
    ]
    
    # 添加 pyJianYingDraft assets
    if pyjy_assets and pyjy_assets.exists():
        args.append(f'--add-data={pyjy_assets}{separator}pyJianYingDraft/assets')
        print("已添加 pyJianYingDraft assets 到打包配置")
    
    # 检查图标文件是否存在
    icon_path = Path('resources/icon.ico')
    if icon_path.exists():
        args.append(f'--icon={icon_path}')
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("打包完成！")
        print(f"可执行文件位于: {Path('dist/CozeJianYingDraftGenerator.exe').absolute()}")
        print("=" * 60)
    except Exception as e:
        print(f"\n打包失败: {e}")
        raise


def create_resources_dir():
    """创建resources目录（如果不存在）"""
    resources_dir = Path('resources')
    resources_dir.mkdir(exist_ok=True)
    print(f"资源目录: {resources_dir.absolute()}")


def main():
    """主函数"""
    print("=" * 60)
    print("Coze剪映草稿生成器 - 打包工具")
    print("=" * 60)
    
    # 创建必要的目录
    create_resources_dir()
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 构建exe
    build_exe()


if __name__ == '__main__':
    main()
