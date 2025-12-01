"""
打包脚本 - 使用PyInstaller将应用打包为exe
"""

import shutil
import sys
from pathlib import Path

import PyInstaller.__main__

# 设置 UTF-8 编码以支持中文输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        # Python 3.6 及更早版本不支持 reconfigure
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist"]
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)


def build_exe(fast_mode=False):
    """构建exe文件"""
    print(f"开始打包应用程序... (模式: {'快速/开发' if fast_mode else '完整/发布'})")

    # 根据操作系统确定路径分隔符 (Windows: ';', Linux/Mac: ':')
    import os

    separator = ";" if os.name == "nt" else ":"

    # 获取 pyJianYingDraft 的 assets 路径
    try:
        import pyJianYingDraft

        pyjy_path = Path(pyJianYingDraft.__file__).parent
        pyjy_assets = pyjy_path / "assets"
        print(f"找到 pyJianYingDraft assets: {pyjy_assets}")
    except Exception as e:
        print(f"警告: 无法找到 pyJianYingDraft assets: {e}")
        pyjy_assets = None

    # 获取 customtkinter 的路径
    try:
        import customtkinter
        ctk_path = Path(customtkinter.__file__).parent
        print(f"找到 customtkinter: {ctk_path}")
    except Exception as e:
        print(f"警告: 无法找到 customtkinter: {e}")
        ctk_path = None

    # PyInstaller参数
    args = [
        "app/main.py",  # 主程序入口
        "--name=CozeJianYingDraftGenerator",  # 应用名称
        "--windowed",  # 不显示控制台窗口
        "--hidden-import=tkinter",  # 确保包含tkinter
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=pyJianYingDraft",  # 添加pyJianYingDraft库
        "--hidden-import=customtkinter",  # 添加customtkinter库
        "--hidden-import=uvicorn",  # 添加uvicorn
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=fastapi",  # 添加fastapi
        "--hidden-import=pydantic",  # 添加pydantic
        "--hidden-import=requests",  # 添加requests
        "--hidden-import=pyngrok",  # 添加pyngrok
        "--hidden-import=dotenv",  # 添加python-dotenv
        "--hidden-import=rich",  # 添加rich
        "--hidden-import=click",  # 添加click
        "--hidden-import=multipart",  # 添加python-multipart
        "--hidden-import=websockets",  # 添加websockets (uvicorn依赖)
        "--noconfirm",  # 不询问确认
    ]

    if fast_mode:
        # 快速模式：使用文件夹模式，不清理缓存
        args.append("--onedir")
        print("使用 --onedir 模式 (构建速度快，生成文件夹)")
    else:
        # 发布模式：使用单文件模式，清理缓存
        args.append("--onefile")
        args.append("--clean")
        print("使用 --onefile 模式 (构建速度慢，生成单文件)")

    # 添加 pyJianYingDraft assets
    if pyjy_assets and pyjy_assets.exists():
        args.append(f"--add-data={pyjy_assets}{separator}pyJianYingDraft/assets")
        print("已添加 pyJianYingDraft assets 到打包配置")

    # 添加 customtkinter assets
    if ctk_path and ctk_path.exists():
        args.append(f"--add-data={ctk_path}{separator}customtkinter")
        print("已添加 customtkinter assets 到打包配置")

    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("打包完成！")

        if fast_mode:
            dist_path = Path("dist/CozeJianYingDraftGenerator/CozeJianYingDraftGenerator.exe").absolute()
        else:
            dist_path = Path("dist/CozeJianYingDraftGenerator.exe").absolute()

        print(f"可执行文件位于: {dist_path}")
        print("=" * 60)
    except Exception as e:
        print(f"\n打包失败: {e}")
        raise


def main():
    """主函数"""
    print("=" * 60)
    print("Coze剪映草稿生成器 - 打包工具")
    print("=" * 60)

    # 检查是否开启快速模式
    fast_mode = "--fast" in sys.argv

    # 只有在非快速模式下才清理旧的构建文件
    if not fast_mode:
        clean_build_dirs()
    else:
        print("快速模式：跳过清理构建目录")

    # 构建exe
    build_exe(fast_mode=fast_mode)


if __name__ == "__main__":
    main()
