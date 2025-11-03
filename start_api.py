"""
简单的 API 服务启动脚本
"""
import subprocess
import sys
from pathlib import Path

def main():
    """启动 FastAPI 服务"""
    print("=" * 60)
    print("🚀 启动 FastAPI 服务")
    print("=" * 60)
    print()
    print("📌 服务地址: http://127.0.0.1:8000")
    print("📌 API 文档: http://127.0.0.1:8000/docs")
    print("📌 ReDoc: http://127.0.0.1:8000/redoc")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    try:
        # 使用 uvicorn 启动服务
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.api_main:app",
            "--reload",
            "--host", "127.0.0.1",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 服务已停止")
        print("=" * 60)

if __name__ == "__main__":
    main()
