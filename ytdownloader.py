import os
import re
import subprocess
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from moviepy.editor import AudioFileClip
import tkinter.ttk as ttk
import tkinter.font as tkfont

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()

def is_valid_youtube_url(url):
    pattern = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w\-]{11}(&.*)?$'
    )
    return bool(pattern.match(url))

def convert_to_mp3(video_path, output_folder, title, progress_queue, progress_bar):
    try:
        base_title = sanitize_filename(title)
        mp3_filename = base_title + ".mp3"
        mp3_path = os.path.join(output_folder, mp3_filename)

        progress_queue.put("Converting audio to MP3...")
        progress_bar.config(mode='indeterminate')
        progress_bar.start(10)

        audio = AudioFileClip(video_path)
        audio.write_audiofile(mp3_path)
        audio.close()

        os.remove(video_path)
        progress_bar.stop()
        progress_queue.put(f"✅ Converted to MP3: {mp3_path}")
    except Exception as e:
        progress_bar.stop()
        progress_queue.put(f"❌ Conversion failed: {e}")

def download_youtube_audio(url, output_folder, progress_queue, progress_bar):
    command = [
        "yt-dlp",
        "--max-downloads", "1",
        "--match-filter", "duration < 540",
        "-f", "bestaudio",
        "-o", os.path.join(output_folder, "%(title)s.%(ext)s"),
        url
    ]
    try:
        progress_queue.put("Downloading audio from YouTube...")
        progress_bar.config(mode='determinate', maximum=100)
        progress_bar['value'] = 0

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        progress_regex = re.compile(r"\[download\]\s+(\d{1,3}\.\d)%")

        for line in process.stdout:
            progress_queue.put(line.strip())
            match = progress_regex.search(line)
            if match:
                percent = float(match.group(1))
                progress_queue.put(("progress_update", percent))

        process.wait()
        if process.returncode not in [0, 101]:
            progress_queue.put(f"⚠️ Download error (code {process.returncode})")
            return False

        progress_bar['value'] = 100
        return True
    except Exception as e:
        progress_queue.put(f"⚠️ Error during download: {e}")
        return False

def find_latest_file(folder):
    files = [os.path.join(folder, f) for f in os.listdir(folder)]
    files = [f for f in files if os.path.isfile(f) and f.lower().endswith(('.webm', '.m4a'))]
    return max(files, key=os.path.getctime) if files else None

def worker_thread(url, output_folder, progress_queue, progress_bar):
    success = download_youtube_audio(url, output_folder, progress_queue, progress_bar)
    if not success:
        progress_queue.put("❌ Download failed. Operation aborted.")
        return
    latest_file = find_latest_file(output_folder)
    if latest_file:
        title = os.path.splitext(os.path.basename(latest_file))[0]
        convert_to_mp3(latest_file, output_folder, title, progress_queue, progress_bar)
    else:
        progress_queue.put("❌ No valid audio file found for conversion.")

def start_download_thread(url, output_folder):
    if not url:
        messagebox.showwarning("Input Error", "Please enter a YouTube link.")
        return
    if not is_valid_youtube_url(url):
        messagebox.showerror("Invalid URL", "The URL provided is not a valid YouTube video link.")
        return
    if not os.path.isdir(output_folder):
        messagebox.showwarning("Folder Error", "The selected folder does not exist.")
        return

    download_btn.config(state="disabled")
    url_entry.config(state="disabled")
    folder_entry.config(state="disabled")
    browse_btn.config(state="disabled")

    status_box.delete('1.0', tk.END)
    progress_bar['value'] = 0

    threading.Thread(target=worker_thread, args=(url, output_folder, progress_queue, progress_bar), daemon=True).start()
    root.after(100, process_queue)

def process_queue():
    try:
        while True:
            msg = progress_queue.get_nowait()
            if isinstance(msg, tuple) and msg[0] == "progress_update":
                progress_bar['value'] = msg[1]
            else:
                status_box.insert(tk.END, msg + "\n")
                status_box.see(tk.END)
    except queue.Empty:
        pass

    if threading.active_count() > 1:
        root.after(100, process_queue)
    else:
        progress_bar.config(mode='indeterminate')
        progress_bar.stop()
        progress_bar['value'] = 0

        download_btn.config(state="normal")
        url_entry.config(state="normal")
        folder_entry.config(state="normal")
        browse_btn.config(state="normal")

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_folder_var.set(folder_selected)

def on_drop(event):
    dropped = event.data
    if dropped.startswith("{") and dropped.endswith("}"):
        dropped = dropped[1:-1]
    url = dropped.split()[0]
    url_entry.delete(0, tk.END)
    url_entry.insert(0, url)


# ---------- UI SETUP ----------
root = TkinterDnD.Tk()
root.title("YouTube to MP3 Converter")
root.iconbitmap("icon.ico")  # Ensure icon.ico exists
root.geometry("600x500")
root.resizable(False, False)

# ---- Styling Section ----
style = ttk.Style(root)
root.configure(bg="#2E3440")
style.theme_use('clam')

default_font = tkfont.Font(family="Segoe UI", size=11)
root.option_add("*Font", default_font)

style.configure("TButton",
                background="#88C0D0",
                foreground="#2E3440",
                borderwidth=0,
                focusthickness=3,
                focuscolor="#81A1C1",
                padding=6)

style.map("TButton",
          background=[('active', '#81A1C1')],
          foreground=[('disabled', '#a0a0a0')])

style.configure("TProgressbar",
                troughcolor="#4C566A",
                background="#88C0D0",
                thickness=20)

# Widgets
tk.Label(root, text="Paste YouTube link (video < 9 mins):", bg="#2E3440", fg="#D8DEE9").pack(padx=10, pady=(10,0))

url_entry = tk.Entry(root, width=60, bg="#3B4252", fg="#D8DEE9", insertbackground="#D8DEE9", relief="flat")
url_entry.pack(padx=10, pady=5)
url_entry.drop_target_register(DND_FILES)
url_entry.dnd_bind('<<Drop>>', on_drop)

output_folder_var = tk.StringVar(value=os.path.abspath("converted"))

folder_frame = tk.Frame(root, bg="#2E3440")
folder_frame.pack(padx=10, pady=5, fill="x")

tk.Label(folder_frame, text="Save MP3 to folder:", bg="#2E3440", fg="#D8DEE9").pack(side="left")
folder_entry = tk.Entry(folder_frame, textvariable=output_folder_var, width=45, bg="#3B4252", fg="#D8DEE9", insertbackground="#D8DEE9", relief="flat")
folder_entry.pack(side="left", padx=(5,0))
browse_btn = tk.Button(folder_frame, text="Browse", command=browse_folder)
browse_btn.pack(side="left", padx=5)

download_btn = tk.Button(root, text="Download & Convert",
                         command=lambda: start_download_thread(url_entry.get().strip(), output_folder_var.get()))
download_btn.pack(padx=10, pady=10)

status_box = tk.Text(root, height=12, width=70, bg="#3B4252", fg="#D8DEE9", relief="flat", highlightthickness=0, insertbackground="#D8DEE9")
status_box.pack(padx=10, pady=(0,5))

progress_bar = ttk.Progressbar(root, mode='indeterminate')
progress_bar.pack(padx=10, pady=(0,10), fill='x')

progress_queue = queue.Queue()

root.mainloop()
