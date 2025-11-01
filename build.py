"""
打包脚本 - 使用PyInstaller将应用打包为exe
支持打包GUI和CLI两个版本
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


def get_common_args():
    """获取通用的PyInstaller参数"""
    # 根据操作系统确定路径分隔符 (Windows: ';', Linux/Mac: ':')
    import os
    separator = ';' if os.name == 'nt' else ':'
    
    # 获取 pyJianYingDraft 的 assets 路径
    pyjy_assets = None
    try:
        import pyJianYingDraft
        pyjy_path = Path(pyJianYingDraft.__file__).parent
        pyjy_assets = pyjy_path / 'assets'
        print(f"找到 pyJianYingDraft assets: {pyjy_assets}")
    except Exception as e:
        print(f"警告: 无法找到 pyJianYingDraft assets: {e}")
    
    common_args = [
        '--clean',                   # 清理临时文件
        f'--add-data=resources{separator}resources',  # 添加资源文件
        '--hidden-import=tkinter',   # 确保包含tkinter
        '--hidden-import=tkinter.ttk',
        '--hidden-import=tkinter.scrolledtext',
        '--hidden-import=pyJianYingDraft',  # 添加pyJianYingDraft库
        '--hidden-import=click',     # CLI依赖
        '--hidden-import=rich',      # CLI依赖
        '--noconfirm',               # 不询问确认
    ]
    
    # 添加 pyJianYingDraft assets
    if pyjy_assets and pyjy_assets.exists():
        common_args.append(f'--add-data={pyjy_assets}{separator}pyJianYingDraft/assets')
        print("已添加 pyJianYingDraft assets 到打包配置")
    
    # 检查图标文件是否存在
    icon_path = Path('resources/icon.ico')
    if icon_path.exists():
        common_args.append(f'--icon={icon_path}')
    
    return common_args, separator


def build_gui():
    """构建GUI版本的exe文件"""
    print("\n" + "=" * 60)
    print("开始打包GUI应用程序...")
    print("=" * 60)
    
    common_args, separator = get_common_args()
    
    # PyInstaller参数 - GUI版本
    args = [
        'src/GUI/main.py',           # GUI主程序入口
        '--name=CozeJianYingDraftGenerator-GUI',  # 应用名称
        '--windowed',                # 不显示控制台窗口
        '--onefile',                 # 打包成单个exe文件
    ] + common_args
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("GUI版本打包完成！")
        print(f"可执行文件位于: {Path('dist/CozeJianYingDraftGenerator-GUI.exe').absolute()}")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"\nGUI版本打包失败: {e}")
        return False


def build_cli():
    """构建CLI版本的exe文件"""
    print("\n" + "=" * 60)
    print("开始打包CLI应用程序...")
    print("=" * 60)
    
    common_args, separator = get_common_args()
    
    # PyInstaller参数 - CLI版本
    args = [
        'src/CLI/main.py',           # CLI主程序入口
        '--name=CozeJianYingDraftGenerator-CLI',  # 应用名称
        '--console',                 # 显示控制台窗口
        '--onefile',                 # 打包成单个exe文件
    ] + common_args
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("CLI版本打包完成！")
        print(f"可执行文件位于: {Path('dist/CozeJianYingDraftGenerator-CLI.exe').absolute()}")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"\nCLI版本打包失败: {e}")
        return False


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
    
    # 构建GUI和CLI版本
    gui_success = build_gui()
    cli_success = build_cli()
    
    # 输出最终结果
    print("\n" + "=" * 60)
    print("打包总结:")
    print("=" * 60)
    print(f"GUI版本: {'✓ 成功' if gui_success else '✗ 失败'}")
    print(f"CLI版本: {'✓ 成功' if cli_success else '✗ 失败'}")
    print("=" * 60)
    
    if gui_success and cli_success:
        print("\n所有版本打包成功！")
        print(f"输出目录: {Path('dist').absolute()}")
    else:
        print("\n部分版本打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()
