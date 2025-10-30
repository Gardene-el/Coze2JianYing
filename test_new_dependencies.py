#!/usr/bin/env python3
"""
测试新添加的依赖项是否正常工作
运行: python test_new_dependencies.py
"""

import sys

def test_click():
    """测试 Click"""
    print("=" * 50)
    print("测试 Click (CLI 框架)")
    print("=" * 50)
    try:
        import click
        print(f"✓ Click 导入成功 (version {click.__version__})")
        
        @click.command()
        @click.option('--name', default='World', help='Name to greet')
        def hello(name):
            click.echo(f'Hello {name}!')
        
        print("✓ Click 命令定义成功")
        return True
    except Exception as e:
        print(f"✗ Click 测试失败: {e}")
        return False

def test_rich():
    """测试 Rich"""
    print("\n" + "=" * 50)
    print("测试 Rich (终端美化)")
    print("=" * 50)
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        console.print("✓ Rich 导入成功")
        
        # 测试彩色输出
        console.print("[bold green]✓[/bold green] 彩色输出测试")
        console.print("[bold yellow]⚠[/bold yellow] 警告样式测试")
        console.print("[bold red]✗[/bold red] 错误样式测试")
        
        # 测试表格
        table = Table(title="测试表格")
        table.add_column("列1", style="cyan")
        table.add_column("列2", style="magenta")
        table.add_row("数据1", "数据2")
        console.print(table)
        
        # 测试面板
        panel = Panel("[bold cyan]Rich 面板测试[/bold cyan]", expand=False)
        console.print(panel)
        
        return True
    except Exception as e:
        print(f"✗ Rich 测试失败: {e}")
        return False

def test_sphinx():
    """测试 Sphinx"""
    print("\n" + "=" * 50)
    print("测试 Sphinx (文档生成器)")
    print("=" * 50)
    try:
        import sphinx
        
        print(f"✓ Sphinx 导入成功 (version {sphinx.__version__})")
        
        # 可选包测试
        try:
            import sphinx_rtd_theme
            print(f"✓ sphinx-rtd-theme 导入成功")
        except ImportError:
            print(f"⚠ sphinx-rtd-theme 未安装（可选）")
        
        try:
            import sphinx_autodoc_typehints
            print(f"✓ sphinx-autodoc-typehints 导入成功")
        except ImportError:
            print(f"⚠ sphinx-autodoc-typehints 未安装（可选）")
        
        return True
    except Exception as e:
        print(f"✗ Sphinx 测试失败: {e}")
        return False

def test_fastapi():
    """测试 FastAPI"""
    print("\n" + "=" * 50)
    print("测试 FastAPI (API 框架)")
    print("=" * 50)
    try:
        import fastapi
        from fastapi import FastAPI
        from pydantic import BaseModel
        import pydantic
        import uvicorn
        
        print(f"✓ FastAPI 导入成功 (version {fastapi.__version__})")
        print(f"✓ Pydantic 导入成功 (version {pydantic.__version__})")
        print(f"✓ Uvicorn 导入成功 (version {uvicorn.__version__})")
        
        # 创建简单的 FastAPI 应用
        app = FastAPI()
        
        class Item(BaseModel):
            name: str
            price: float
        
        @app.get("/")
        def root():
            return {"message": "Hello World"}
        
        print("✓ FastAPI 应用创建成功")
        return True
    except Exception as e:
        print(f"✗ FastAPI 测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试新添加的依赖项...\n")
    
    results = {
        "Click": test_click(),
        "Rich": test_rich(),
        "Sphinx": test_sphinx(),
        "FastAPI": test_fastapi(),
    }
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:15} {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有依赖项测试通过！")
        return 0
    else:
        print(f"\n[FAILED] {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
