import os
import math
import time
import shutil
from yt_dlp import YoutubeDL

class YouTubeDownloader:
    def __init__(self, url, quality="highest", save_path=None, file_format="mp4"):
        self.url = url
        self.quality = quality
        self.save_path = save_path or self.get_default_save_path()
        self.file_format = file_format
        self.start_time = time.time()
        self.last_printed_percentage = 0
        self.ffmpeg_installed = self.check_ffmpeg()

    def get_default_save_path(self):
        return os.path.join(os.path.expanduser("~"), "Desktop")

    def check_ffmpeg(self):
        """Check if ffmpeg is installed and accessible."""
        return shutil.which('ffmpeg') is not None

    def format_bytes(self, bytes_num):
        if bytes_num == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(bytes_num, 1024)))
        p = math.pow(1024, i)
        s = round(bytes_num / p, 2)
        return f"{s} {size_name[i]}"

    def format_time(self, seconds):
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                percentage = downloaded_bytes / total_bytes * 100
                if percentage - self.last_printed_percentage >= 1 or percentage == 100:
                    elapsed_time = time.time() - self.start_time
                    speed = downloaded_bytes / elapsed_time  # bytes per second
                    remaining_time = (total_bytes - downloaded_bytes) / speed if speed > 0 else 0

                    speed_str = self.format_bytes(speed) + "/s"
                    remaining_time_str = self.format_time(remaining_time)
                    total_size_str = self.format_bytes(total_bytes)
                    downloaded_str = self.format_bytes(downloaded_bytes)

                    print(
                        f"\rDownloaded: {downloaded_str} / {total_size_str} "
                        f"({percentage:.2f}%) | Speed: {speed_str} | "
                        f"ETA: {remaining_time_str}",
                        end=''
                    )
                    self.last_printed_percentage = percentage
        elif d['status'] == 'finished':
            print("\nDownload completed successfully.")

    def download_video(self):
        if self.quality == "highest":
            ydl_format = 'bestvideo+bestaudio/best'
        else:
            # Extract numerical part from quality input (e.g., '720p' -> '720')
            height = ''.join(filter(str.isdigit, self.quality))
            ydl_format = f'bestvideo[height<={height}]+bestaudio/best'

        # If ffmpeg is installed, set merge_output_format to the desired file format
        if self.ffmpeg_installed:
            ydl_opts = {
                'format': ydl_format,
                'outtmpl': os.path.join(self.save_path, f'%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'noplaylist': True,
                'merge_output_format': self.file_format,
            }
        else:
            print("FFmpeg не установлен. Будет использоваться наиболее подходящий формат с включенным звуком.")
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(self.save_path, f'%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'noplaylist': True,
            }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                print("Начало загрузки...")
                ydl.download([self.url])
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")

def main():
    url = input("Введите URL видео на YouTube: ").strip()
    quality = input("Введите качество видео (например, 720p) [highest]: ").strip() or "highest"
    save_path = input("Введите путь сохранения [Рабочий стол]: ").strip() or None
    file_format = input("Введите формат видео [mp4]: ").strip() or "mp4"

    downloader = YouTubeDownloader(url, quality, save_path, file_format)
    
    if not downloader.ffmpeg_installed:
        print("\nОбратите внимание: FFmpeg не установлен. Чтобы скачать видео с раздельными аудио и видео потоками, необходимо установить FFmpeg.")
        print("Вы можете скачать FFmpeg с официального сайта: https://ffmpeg.org/download.html")
        print("После установки FFmpeg перезапустите программу.\n")

    downloader.download_video()

if __name__ == "__main__":
        main()