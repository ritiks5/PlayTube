import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pytube

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Downloader")

        self.url_label = tk.Label(root, text="Playlist URL:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        self.submit_button = tk.Button(root, text="Submit", command=self.fetch_streams)
        self.submit_button.pack(pady=5)

        self.quality_label = tk.Label(root, text="Select Quality:")
        self.quality_label.pack(pady=5)

        self.quality_var = tk.StringVar(root)
        self.quality_dropdown = ttk.Combobox(root, textvariable=self.quality_var)
        self.quality_dropdown.pack(pady=5)

        self.download_button = tk.Button(root, text="Download", command=self.download_playlist)
        self.download_button.pack(pady=5)

        self.progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', maximum=100)
        self.progress_bar.pack(pady=5)

        self.cancel_button = tk.Button(root, text="Cancel", command=self.cancel_download)
        self.cancel_button.pack(pady=5)

        self.stream_list = []
        self.playlist = None
        self.selected_stream = None
        self.download_thread = None
        self.cancel_event = threading.Event()

    def fetch_streams(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a playlist URL.")
            return

        try:
            self.playlist = pytube.Playlist(url)
            first_video = pytube.YouTube(self.playlist.video_urls[0])
            self.stream_list = list(first_video.streams.filter(progressive=True))
            stream_options = [f"{stream.resolution} / {stream.mime_type}" for stream in self.stream_list]
            self.quality_dropdown['values'] = stream_options
            if stream_options:
                self.quality_dropdown.current(0)
            messagebox.showinfo("Streams Fetched", "Available qualities for the first video are listed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch streams: {e}")

    def download_playlist(self):
        quality = self.quality_var.get()
        if not quality:
            messagebox.showwarning("Selection Error", "Please select a video quality.")
            return

        selected_index = self.quality_dropdown.current()
        self.selected_stream = self.stream_list[selected_index]

        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(self.playlist.video_urls)
        self.cancel_event.clear()

        self.download_thread = threading.Thread(target=self.download_videos)
        self.download_thread.start()

    def download_videos(self):
        try:
            for i, video_url in enumerate(self.playlist.video_urls):
                if self.cancel_event.is_set():
                    break
                youtube = pytube.YouTube(video_url)
                stream = youtube.streams.get_by_itag(self.selected_stream.itag)
                stream.download()
                self.progress_bar['value'] += 1
                print(f"Downloaded: {youtube.title}")
            messagebox.showinfo("Download Complete", f"Downloaded {self.progress_bar['value']} out of {len(self.playlist.video_urls)} videos.")
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download videos: {e}")

    def cancel_download(self):
        if self.download_thread is not None and self.download_thread.is_alive():
            self.cancel_event.set()
            self.download_thread.join()
            messagebox.showinfo("Download Canceled", f"Download canceled after {self.progress_bar['value']} videos.")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
