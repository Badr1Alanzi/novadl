from pathlib import Path
from typing import Optional, Union

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from novadl.const import APP_NAME, APP_VERSION
from novadl.core import DownloadResult, MediaInfo, MediaType, PlaylistInfo

novadl_theme = Theme({"info": "bold cyan", "success": "bold green", "warning": "bold yellow", "error": "bold red", "title": "bold white", "path": "blue", "url": "underline blue", "dim": "dim white", "highlight": "magenta"})
console = Console(theme=novadl_theme, highlight=False, legacy_windows=False)


def show_welcome() -> None:
    text = Text()
    text.append(f"{APP_NAME} v{APP_VERSION}", style="bold cyan")
    text.append("\nA powerful CLI downloader for video and audio")
    console.print(Panel(text, border_style="cyan"))


def show_info(info: Union[MediaInfo, PlaylistInfo]) -> None:
    if isinstance(info, PlaylistInfo):
        _show_playlist(info)
    else:
        _show_media(info)


def _show_media(info: MediaInfo) -> None:
    t = Table(box=box.ROUNDED, title="Media Information", title_style="bold cyan")
    t.add_column("Property", style="cyan")
    t.add_column("Value", style="white")
    t.add_row("Title", info.title)
    t.add_row("Duration", info.duration_str)
    t.add_row("Uploader", info.uploader or "N/A")
    t.add_row("Upload Date", info.upload_date or "N/A")
    t.add_row("Source", info.webpage_url or info.url)
    t.add_row("Extractor", info.extractor or "N/A")
    if info.formats:
        t.add_row("Available Formats", str(len(info.formats)))
    if info.subtitles:
        t.add_row("Subtitles", ", ".join(info.subtitles.keys()))
    console.print(t)
    console.print()


def _show_playlist(info: PlaylistInfo) -> None:
    t = Table(box=box.ROUNDED, title="Playlist Information", title_style="bold cyan")
    t.add_column("Property", style="cyan")
    t.add_column("Value", style="white")
    t.add_row("Title", info.title)
    t.add_row("Uploader", info.uploader or "N/A")
    t.add_row("Entries", str(info.entry_count))
    t.add_row("Source", info.webpage_url or info.url)
    console.print(t)
    if info.entries:
        et = Table(box=box.SIMPLE, title="Entries", title_style="bold")
        et.add_column("#", style="dim")
        et.add_column("Title", style="white")
        et.add_column("Duration", style="cyan")
        for i, e in enumerate(info.entries[:50], 1):
            et.add_row(str(i), e.title, e.duration_str or "N/A")
        console.print(et)
        if info.entry_count > 50:
            console.print(f"[dim]... and {info.entry_count - 50} more[/dim]")
    console.print()


def show_download_result(result: DownloadResult) -> None:
    if result.success:
        console.print(f"[success]OK Downloaded:[/success] {result.title}")
        console.print(f"  [dim]Path:[/dim] [path]{result.file_path}[/path]")
        console.print(f"  [dim]Size:[/dim] {_fmt_size(result.file_size)}")
    else:
        console.print(f"[error]FAIL Failed:[/error] {result.title}")
        console.print(f"  [error]Reason:[/error] {result.error_message}")
    console.print()


def show_history(entries: list[DownloadResult]) -> None:
    if not entries:
        console.print("[dim]No download history found.[/dim]")
        return
    t = Table(box=box.ROUNDED, title="Download History", title_style="bold cyan")
    t.add_column("#", style="dim")
    t.add_column("Title", style="white")
    t.add_column("Type", style="cyan")
    t.add_column("Size", style="white")
    t.add_column("Status", style="bold")
    for i, e in enumerate(entries[:20], 1):
        t.add_row(str(i), e.title[:50], "Video" if e.media_type == MediaType.VIDEO else "Audio", _fmt_size(e.file_size), "[success]OK[/success]" if e.success else "[error]FAIL[/error]")
    console.print(t)
    if len(entries) > 20:
        console.print(f"[dim]... and {len(entries) - 20} more[/dim]")
    console.print()


def show_config(data: dict[str, str]) -> None:
    if not data:
        console.print("[dim]No configuration set. All defaults apply.[/dim]")
        return
    t = Table(box=box.ROUNDED, title="Current Configuration", title_style="bold cyan")
    t.add_column("Key", style="cyan")
    t.add_column("Value", style="white")
    for k, v in sorted(data.items()):
        t.add_row(k, v)
    console.print(t)
    console.print()


def show_diagnosis(ffmpeg_installed: bool, ffmpeg_version: Optional[str], yt_dlp_version: str) -> None:
    t = Table(box=box.ROUNDED, title="System Diagnosis", title_style="bold cyan")
    t.add_column("Component", style="cyan")
    t.add_column("Status", style="bold")
    t.add_column("Version", style="white")
    yt = "[success]OK[/success]" if yt_dlp_version != "unknown" else "[error]FAIL[/error]"
    ff = "[success]OK[/success]" if ffmpeg_installed else "[warning]FAIL Not found[/warning]"
    t.add_row("yt-dlp", yt, yt_dlp_version)
    t.add_row("FFmpeg", ff, ffmpeg_version or "N/A")
    console.print(t)
    console.print()


def create_progress() -> Progress:
    return Progress(TextColumn("[progress.description]{task.description}"), BarColumn(), DownloadColumn(), TransferSpeedColumn(), TimeRemainingColumn(), transient=False)


def make_progress_hook(progress: Progress, task_id: int):
    def hook(d: dict) -> None:
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            progress.update(task_id, completed=d.get("downloaded_bytes", 0), total=total)
        elif d["status"] == "finished":
            total = d.get("total_bytes") or 0
            progress.update(task_id, completed=total)
    return hook


def _fmt_size(size: int) -> str:
    if size == 0:
        return "N/A"
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
