"""
Coze剪映草稿生成器 - CLI主程序入口
"""
import sys
import os
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from utils.logger import setup_logger, get_logger
from utils.draft_generator import DraftGenerator

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="Coze剪映草稿生成器")
def cli():
    """
    Coze剪映草稿生成器 - 命令行工具
    
    将Coze导出的JSON数据转换为剪映草稿文件
    """
    pass


@cli.command()
@click.argument('json_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出目录路径')
@click.option('--verbose', '-v', is_flag=True, help='显示详细日志')
def generate(json_file, output, verbose):
    """
    从JSON文件生成剪映草稿
    
    JSON_FILE: Coze导出的JSON文件路径
    """
    # 设置日志
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    setup_logger(log_dir / "app_cli.log")
    logger = get_logger(__name__)
    
    console.print(Panel.fit(
        "[bold cyan]Coze剪映草稿生成器 CLI[/bold cyan]",
        subtitle="正在处理您的请求..."
    ))
    
    try:
        # 验证JSON文件
        json_path = Path(json_file)
        if not json_path.exists():
            console.print(f"[bold red]✗ 文件不存在: {json_path}[/bold red]")
            sys.exit(1)
        
        if verbose:
            console.print(f"[green]✓[/green] JSON文件: {json_path}")
        
        # 初始化草稿生成器
        draft_generator = DraftGenerator()
        
        # 设置输出目录
        if output:
            output_path = Path(output)
        else:
            output_path = Path.cwd() / "output"
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        if verbose:
            console.print(f"[green]✓[/green] 输出目录: {output_path}")
        
        # 生成草稿
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在生成草稿...", total=None)
            
            result = draft_generator.generate_from_file(
                str(json_path),
                str(output_path)
            )
            
            progress.update(task, completed=True)
        
        if result:
            console.print(f"\n[bold green]✓ 草稿生成成功！[/bold green]")
            console.print(f"输出目录: {output_path}")
            console.print(f"生成的草稿: {len(result)} 个")
        else:
            console.print(f"\n[bold red]✗ 草稿生成失败[/bold red]")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"生成草稿时出错: {e}", exc_info=True)
        console.print(f"\n[bold red]✗ 错误: {e}[/bold red]")
        sys.exit(1)


@cli.command()
def info():
    """显示程序信息"""
    console.print(Panel(
        "[bold cyan]Coze剪映草稿生成器 CLI[/bold cyan]\n\n"
        "版本: 0.1.0\n"
        "功能: 将Coze导出的JSON数据转换为剪映草稿文件\n\n"
        "[dim]使用 --help 查看详细帮助信息[/dim]",
        title="程序信息",
        border_style="cyan"
    ))


def main():
    """主函数"""
    cli()


if __name__ == "__main__":
    main()
