import sys
from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from novadl.const import APP_AUTHOR, APP_GITHUB, APP_NAME, APP_VERSION, APP_X, NovaDLError
from novadl.core import DownloadUseCase, ExtractInfoUseCase, UpdateUseCase
from novadl.infra import ConfigManager, FFmpegChecker, HistoryManager, YtDlpDownloader
from novadl.ui import (
    console,
    create_progress,
    make_progress_hook,
    show_config,
    show_diagnosis,
    show_download_result,
    show_history,
    show_info,
    show_welcome,
)

_downloader = YtDlpDownloader()
_config = ConfigManager()
_history = HistoryManager()
_download_uc = DownloadUseCase(_downloader, _config, _history)
_info_uc = ExtractInfoUseCase(_downloader)
_update_uc = UpdateUseCase(_downloader)


def _validate_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        raise typer.BadParameter("URL must start with http:// or https://")
    return url


def _resolve_output_dir(path: Optional[str]) -> Optional[Path]:
    if path is None:
        return None
    p = path.strip()
    if not p:
        return None
    return Path(p).resolve()


def _validate_cookies(path: Optional[str]) -> Optional[Path]:
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        raise typer.BadParameter(f"Cookies file not found: {path}")
    return p


# ─── Commands ──────────────────────────────────────────────

def download(
    url: str = typer.Argument(..., help="URL of the video to download", callback=_validate_url),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory", callback=_resolve_output_dir),
    quality: Optional[str] = typer.Option(None, "--quality", "-q", help="Video quality"),
    output_format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format (mp4, mkv, webm)"),
    audio_only: bool = typer.Option(False, "--audio-only", "-a", help="Download audio only"),
    audio_format: str = typer.Option("mp3", "--audio-format", help="Audio format (mp3, m4a, opus, flac, wav)"),
    audio_quality: str = typer.Option("192", "--audio-quality", help="Audio quality in kbps"),
    subtitles: bool = typer.Option(False, "--subtitles", "-s", help="Download subtitles"),
    subtitle_langs: Optional[str] = typer.Option(None, "--sub-langs", help="Subtitle language codes (comma separated)"),
    embed_subs: bool = typer.Option(False, "--embed-subs", help="Embed subtitles into video"),
    write_thumbnail: bool = typer.Option(False, "--thumbnail", "-t", help="Write thumbnail"),
    cookies: Optional[str] = typer.Option(None, "--cookies", "-c", help="Path to cookies file", callback=_validate_cookies),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy URL"),
) -> None:
    try:
        with create_progress() as progress:
            task_id = progress.add_task(f"[cyan]Downloading:[/cyan] {url[:60]}", total=None)
            hook = make_progress_hook(progress, task_id)
            langs = subtitle_langs.split(",") if subtitle_langs and subtitle_langs.strip() else None
            result = _download_uc.execute_single(url=url, output_dir=output_dir, quality=quality, audio_only=audio_only, audio_format=audio_format, audio_quality=audio_quality, output_format=output_format, subtitles=subtitles, subtitle_langs=langs, embed_subs=embed_subs, write_thumbnail=write_thumbnail, cookies_file=cookies, proxy_url=proxy, progress_callback=hook)
        show_download_result(result)
    except NovaDLError as e:
        console.print(f"[error]Error:[/error] {e}")
        raise typer.Exit(1)


def audio(
    url: str = typer.Argument(..., help="URL to extract audio from", callback=_validate_url),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory", callback=_resolve_output_dir),
    audio_format: str = typer.Option("mp3", "--format", "-f", help="Audio format (mp3, m4a, opus, flac, wav)"),
    audio_quality: str = typer.Option("192", "--quality", "-q", help="Audio quality in kbps"),
    cookies: Optional[str] = typer.Option(None, "--cookies", "-c", help="Path to cookies file", callback=_validate_cookies),
    proxy: Optional[str] = typer.Option(None, "--proxy", "-p", help="Proxy URL"),
) -> None:
    try:
        with create_progress() as progress:
            task_id = progress.add_task("[cyan]Extracting audio:[/cyan]", total=None)
            result = _download_uc.execute_single(url=url, output_dir=output_dir, audio_only=True, audio_format=audio_format, audio_quality=audio_quality, cookies_file=cookies, proxy_url=proxy, progress_callback=make_progress_hook(progress, task_id))
        show_download_result(result)
    except NovaDLError as e:
        console.print(f"[error]Error:[/error] {e}")
        raise typer.Exit(1)


def info(url: str = typer.Argument(..., help="URL to extract information from", callback=_validate_url)) -> None:
    try:
        show_info(_info_uc.execute(url))
    except NovaDLError as e:
        console.print(f"[error]Error:[/error] {e}")
        raise typer.Exit(1)


def update() -> None:
    try:
        with console.status("[cyan]Updating yt-dlp...[/cyan]"):
            updated = _update_uc.execute()
        console.print("[success]OK yt-dlp updated successfully[/success]" if updated else "[info]yt-dlp is already up to date[/info]")
    except NovaDLError as e:
        console.print(f"[error]Error:[/error] {e}")
        raise typer.Exit(1)


def config(key: Optional[str] = typer.Argument(None, help="Key to view or set"), value: Optional[str] = typer.Argument(None, help="Value to set")) -> None:
    try:
        if key and value:
            _config.set(key, value)
            console.print(f"[success]OK Set {key} = {value}[/success]")
        elif key:
            v = _config.get(key)
            console.print(f"[info]{key}[/info] = [white]{v}[/white]" if v is not None else f"[dim]No value set for '{key}'[/dim]")
        else:
            show_config(_config.get_all())
    except NovaDLError as e:
        console.print(f"[error]Error:[/error] {e}")
        raise typer.Exit(1)


def version() -> None:
    console.print(f"[bold cyan]{APP_NAME}[/bold cyan] [white]v{APP_VERSION}[/white]")
    console.print(f"Author: {APP_AUTHOR}")
    console.print(f"GitHub: {APP_GITHUB}")
    console.print(f"X: {APP_X}")
    console.print(f"yt-dlp: {_downloader.get_version()}")


def history() -> None:
    show_history(_history.get_all())


def clear_history() -> None:
    _history.clear()
    console.print("[success]OK Download history cleared[/success]")


def doctor() -> None:
    import platform
    console.print(f"OS: {platform.system()} {platform.release()}")
    console.print(f"Python: {platform.python_version()}")
    console.print(f"{APP_NAME}: v{APP_VERSION}")
    show_diagnosis(FFmpegChecker.is_installed(), FFmpegChecker.get_version(), _downloader.get_version())
    if not FFmpegChecker.is_installed():
        console.print("[warning]FFmpeg not found[/warning]")
        console.print(FFmpegChecker.get_install_guide())


# ─── Interactive Menu ──────────────────────────────────────

PLATFORMS = [
    ("YouTube", "youtube.com/watch?v="),
    ("TikTok", "tiktok.com/@"),
    ("Instagram", "instagram.com/p/"),
    ("Facebook", "facebook.com/watch/"),
    ("X (Twitter)", "x.com/"),
    ("Vimeo", "vimeo.com/"),
    ("Reddit", "reddit.com/r/"),
    ("Twitch", "twitch.tv/"),
    ("SoundCloud", "soundcloud.com/"),
    ("Custom URL", ""),
]


def _get_dl_dir() -> Path:
    s = _config.get("output_dir")
    return Path(s) if s else Path.home() / "Videos" / "NovaDL"


def _change_path() -> None:
    cur = _get_dl_dir()
    console.print(f"[info]Current path:[/info] [path]{cur}[/path]")
    p = Prompt.ask("[cyan]New path[/cyan]", default=str(cur))
    r = Path(p).resolve()
    r.mkdir(parents=True, exist_ok=True)
    _config.set("output_dir", str(r))
    console.print(f"[success]OK Save path set: {r}[/success]")


def _choose_quality(audio_only: bool = False) -> tuple[str, str]:
    """Returns (quality_format, audio_quality_kbps) tuple."""
    if audio_only:
        t = Table(box=None, show_header=False)
        t.add_column("#", style="dim")
        t.add_column("Audio Quality")
        opts = ["Best", "128k", "192k", "256k", "320k"]
        for i, q in enumerate(opts, 1):
            t.add_row(str(i), q)
        console.print(t)
        m = {"1": "0", "2": "128", "3": "192", "4": "256", "5": "320"}
        aq = m.get(Prompt.ask("[cyan]Choose audio quality[/cyan]", default="1"), "0")
        return "best", aq
    t = Table(box=None, show_header=False)
    t.add_column("#", style="dim")
    t.add_column("Quality")
    for i, q in enumerate(["Best", "1080p", "720p", "480p", "360p", "Worst"], 1):
        t.add_row(str(i), q)
    console.print(t)
    m = {"1": "best", "2": "bestvideo[height<=1080]+bestaudio/best[height<=1080]", "3": "bestvideo[height<=720]+bestaudio/best[height<=720]", "4": "bestvideo[height<=480]+bestaudio/best[height<=480]", "5": "bestvideo[height<=360]+bestaudio/best[height<=360]", "6": "worst"}
    q = m.get(Prompt.ask("[cyan]Choose quality[/cyan]", default="1"), "best")
    return q, "192"


def _dl_interactive(url: str, audio_only: bool = False) -> None:
    d = _get_dl_dir()
    d.mkdir(parents=True, exist_ok=True)
    q, aq = _choose_quality(audio_only)
    af = _config.get("audio_format", "mp3") if audio_only else "mp3"
    try:
        with create_progress() as p:
            t = p.add_task("[cyan]Downloading...[/cyan]", total=None)
            r = _download_uc.execute_single(url=url, output_dir=d, quality=q, audio_only=audio_only, audio_format=af, audio_quality=aq, progress_callback=make_progress_hook(p, t))
        show_download_result(r)
    except NovaDLError as e:
        console.print(f"[error]Error:[/error] {e}")


def _platform_menu() -> None:
    console.print()
    t = Table(box=None, show_header=False, title="Select Platform", title_style="bold cyan")
    t.add_column("#", style="dim")
    t.add_column("Platform")
    for i, (n, _) in enumerate(PLATFORMS, 1):
        t.add_row(str(i), n)
    t.add_row("11", "Change save path")
    t.add_row("12", "Download history")
    t.add_row("13", "System info")
    t.add_row("14", "Exit")
    console.print(t)

    c = Prompt.ask("[cyan]Enter number[/cyan]", default="1")
    if c == "11":
        _change_path(); return
    if c == "12":
        show_history(_history.get_all()); return
    if c == "13":
        doctor(); return
    if c == "14":
        console.print("[info]Goodbye![/info]"); sys.exit(0)

    try:
        idx = int(c) - 1
    except ValueError:
        console.print("[error]Invalid number[/error]")
        return
    if idx < 0 or idx >= len(PLATFORMS):
        console.print("[error]Invalid choice[/error]"); return

    name, hint = PLATFORMS[idx]
    url = Prompt.ask(f"[cyan]Enter {name} URL[/cyan]")
    audio_only = Prompt.ask("[cyan]Video or Audio?[/cyan]", choices=["1", "2"], default="1") == "2"
    console.print(f"[info]Downloading {'audio' if audio_only else 'video'} from {name}[/info]")
    _dl_interactive(url, audio_only)


def interactive_menu() -> None:
    first = True
    while True:
        if first:
            console.print(Panel(f"[bold cyan]{APP_NAME} v{APP_VERSION}[/bold cyan]\nDownload video & audio from YouTube, TikTok, Instagram, and 1000+ sites.\n[dim]Developer: {APP_AUTHOR} | X: {APP_X} | GitHub: {APP_GITHUB}[/dim]", border_style="cyan"))
            first = False
        console.print(f"[dim]Save path: [path]{_get_dl_dir()}[/path][/dim]\n")
        _platform_menu()
        if not Confirm.ask("[cyan]Back to main menu?[/cyan]", default=True):
            console.print("[info]Goodbye![/info]")
            break
        console.print()


# ─── Typer App ─────────────────────────────────────────────

app = typer.Typer(name="novadl", help="NovaDL - A powerful CLI downloader for video and audio from the internet.", no_args_is_help=False, rich_markup_mode="rich", pretty_exceptions_show_locals=False, add_completion=False)
app.command(name="download")(download)
app.command(name="audio")(audio)
app.command(name="info")(info)
app.command(name="update")(update)
app.command(name="config")(config)
app.command(name="version")(version)
app.command(name="history")(history)
app.command(name="clear-history")(clear_history)
app.command(name="doctor")(doctor)


def main() -> None:
    if len(sys.argv) <= 1:
        show_welcome()
        interactive_menu()
    else:
        show_welcome()
        app()
