"""
构建脚本：使用 CPython Embeddable Package 部署 Python 后端。

替代 PyInstaller——不需要维护 hiddenimports，无防病毒误报，
构建产物就是官方 python.exe 加上 pip install 后的 site-packages。

用法（从 monorepo 根目录执行）：
    python scripts/build_workflow/build_python.py

产物将输出到：
    apps/desktop/resources/python/
    ├── python.exe          ← CPython embed 可执行文件
    ├── python312.dll
    ├── python312._pth      ← 已修改：启用 site-packages
    ├── python312.zip       ← 压缩的 stdlib
    ├── Lib/
    │   └── site-packages/  ← pip 安装的全部依赖 + 本项目
    └── ...

Electron 生产模式通过以下命令启动后端：
    python.exe -m src.main --gui-only --port 20210 --host 127.0.0.1
"""

import hashlib
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

# ── 版本配置 ────────────────────────────────────────────────────────────────
PYTHON_VERSION = "3.12.9"
# python{major}{minor}._pth：major=3, minor=12 → python312._pth
PYTHON_VER_SHORT = "".join(PYTHON_VERSION.split(".")[:2])  # "312"
EMBED_ZIP_NAME = f"python-{PYTHON_VERSION}-embed-amd64.zip"
EMBED_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/{EMBED_ZIP_NAME}"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

# ── 路径 ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent.parent  # Coze2JianYing/
DIST_DIR = ROOT / "apps" / "desktop" / "resources" / "python"
CACHE_DIR = ROOT / "build" / "embed_cache"


def compute_stamp() -> str:
    """计算 stamp 内容：Python 版本 + pyproject.toml 的 SHA256。

    Node.js 端（PythonBackendManager）读取此 stamp 与当前
    pyproject.toml 哈希对比，决定是否需要重新构建 embed。
    """
    pyproject = ROOT / "pyproject.toml"
    sha256 = hashlib.sha256(pyproject.read_bytes()).hexdigest()
    return f"python_version={PYTHON_VERSION}\nhash={sha256}\n"


def download(url: str, dest: Path) -> None:
    """下载文件并显示进度。"""
    print(f"  Downloading {dest.name} ...")
    with urllib.request.urlopen(url) as resp, open(dest, "wb") as f:  # noqa: S310
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        block = 65536
        while True:
            chunk = resp.read(block)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded * 100 // total
                print(f"\r  {pct:3d}%  ({downloaded:,}/{total:,} bytes)", end="", flush=True)
    print()


def main() -> None:
    # 1. 清理目标目录（保持幂等）
    print(f"[1/6] Cleaning {DIST_DIR} ...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # 2. 下载 embed zip（本地缓存避免重复下载）
    embed_zip = CACHE_DIR / EMBED_ZIP_NAME
    if not embed_zip.exists():
        print(f"[2/6] Downloading CPython {PYTHON_VERSION} embeddable package ...")
        download(EMBED_URL, embed_zip)
    else:
        print(f"[2/6] Using cached {embed_zip.name}")

    # 3. 解压到目标目录
    print(f"[3/6] Extracting embed package ...")
    with zipfile.ZipFile(embed_zip) as zf:
        zf.extractall(DIST_DIR)

    # 4. 启用 site-packages：取消 ._pth 中 "#import site" 的注释
    #    embed 包默认关闭 site 模块，取消注释后 site.py 会自动把
    #    Lib/site-packages 加入 sys.path，pip 及其安装的包才能被找到。
    pth_file = DIST_DIR / f"python{PYTHON_VER_SHORT}._pth"
    if not pth_file.exists():
        matches = list(DIST_DIR.glob("python*._pth"))
        if not matches:
            print("ERROR: No ._pth file found in embed package!", file=sys.stderr)
            sys.exit(1)
        pth_file = matches[0]
    print(f"[4/6] Patching {pth_file.name} (enabling site-packages) ...")
    content = pth_file.read_text(encoding="utf-8")
    if "#import site" in content:
        patched = content.replace("#import site", "import site")
    elif "import site" not in content:
        # 极少数 embed 版本格式异常，手动追加
        patched = content.rstrip("\n") + "\nimport site\n"
    else:
        patched = content  # 已启用，无需修改
    pth_file.write_text(patched, encoding="utf-8")

    # 5. 引导安装 pip（首次运行时写入 Lib/site-packages/pip/）
    get_pip = CACHE_DIR / "get-pip.py"
    if not get_pip.exists():
        print(f"[5/6] Downloading get-pip.py ...")
        download(GET_PIP_URL, get_pip)
    else:
        print(f"[5/6] Using cached get-pip.py")

    python_exe = DIST_DIR / "python.exe"
    print(f"       Bootstrapping pip ...")
    subprocess.run(
        [str(python_exe), str(get_pip), "--no-warn-script-location"],
        cwd=str(DIST_DIR),
        check=True,
    )

    # 6. pip install 项目本身及其全部依赖
    #    embed zip 不预装 setuptools/wheel，先安装它们，否则
    #    pip install . 调用 setuptools.build_meta 时会报 BackendUnavailable。
    print(f"[6/6] pip install setuptools + project + all dependencies ...")
    subprocess.run(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--no-warn-script-location",
            "setuptools",
            "wheel",
        ],
        cwd=str(DIST_DIR),
        check=True,
    )
    subprocess.run(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--no-warn-script-location",
            str(ROOT),  # 安装当前项目（包含所有 [project.dependencies]）
        ],
        cwd=str(DIST_DIR),
        check=True,
    )

    # ── 验证产物 ─────────────────────────────────────────────────────────────
    site_packages = DIST_DIR / "Lib" / "site-packages"
    ok = (
        python_exe.exists()
        and (site_packages / "fastapi").exists()
        and (site_packages / "src").exists()
    )
    if ok:
        # 写 stamp 文件供 PythonBackendManager 做增量检测
        stamp = DIST_DIR / ".stamp"
        stamp.write_text(compute_stamp(), encoding="utf-8")
        print(f"\n[OK] Embed build success: {DIST_DIR}")
        print(f"     Verify: {python_exe} -m src.main --gui-only --port 20210")
    else:
        missing = [
            p
            for p in [python_exe, site_packages / "fastapi", site_packages / "src"]
            if not p.exists()
        ]
        print(f"\n[FAIL] Build incomplete - missing: {missing}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
