import tkinter as tk
from tkinter import messagebox
import pygame
import vlc
import time
from pydub import AudioSegment

# 读取字幕文件（.srt）
def read_subtitles(filename):
    subtitles = []
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        subtitle = {}
        for line in lines:
            if '-->' in line:
                times = line.split(' --> ')
                subtitle['start'] = times[0].strip()
                subtitle['end'] = times[1].strip()
            elif line.strip() == '':
                subtitles.append(subtitle)
                subtitle = {}
            else:
                subtitle['text'] = line.strip()
    return subtitles

# 获取音频文件时长
def get_audio_duration(filename):
    audio = AudioSegment.from_file(filename)
    return audio.duration_seconds  # 返回音频时长，单位为秒

# 初始化音频和播放器
def play_audio(filename):
    media = vlc.MediaPlayer(filename)
    media.play()
    return media

# 更新进度条和显示字幕
def update_progress(media, progress, label, subtitles, window):
    # 获取音频的当前播放时间
    current_time = media.get_time() / 1000  # 转换为秒
    progress.set(current_time)
    
    # 显示字幕
    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle['start'])
        end_time = time_to_seconds(subtitle['end'])
        if start_time <= current_time <= end_time:
            label.config(text=subtitle['text'])
            break
    window.after(100, update_progress, media, progress, label, subtitles, window)

# 转换时间格式为秒数
def time_to_seconds(t):
    # 替换逗号为点，并分割时间
    t = t.replace(',', '.')
    hours, minutes, seconds = map(float, t.split(':'))
    
    # 计算总秒数
    return hours * 3600 + minutes * 60 + seconds

# 处理点击字幕
def on_subtitle_click(subtitle, media, progress):
    start_time = time_to_seconds(subtitle['start'])
    media.set_time(int(start_time * 1000))  # 设置音频播放时间
    progress.set(start_time)

# 播放/暂停音频
def toggle_play_pause(media, play_button):
    if media.is_playing():
        media.pause()
        play_button.config(text="播放")
    else:
        media.play()
        play_button.config(text="暂停")

# 创建GUI界面
def create_gui(audio_file, subtitle_file):
    window = tk.Tk()
    window.title("Audio Player with Subtitles")
    
    # 获取音频时长并设置进度条最大值
    audio_duration = get_audio_duration(audio_file)

    # 左侧：进度条和画面
    progress = tk.DoubleVar()
    progress_bar = tk.Scale(window, variable=progress, orient=tk.HORIZONTAL, length=400, from_=0, to=audio_duration, sliderlength=20)
    progress_bar.pack(pady=20)

    label = tk.Label(window, text="", font=("Arial", 14), width=50, height=4, anchor="w", justify=tk.LEFT)
    label.pack(pady=10)

    # 右侧：字幕列表
    subtitles = read_subtitles(subtitle_file)
    subtitle_list = tk.Listbox(window, height=15, width=50)
    for subtitle in subtitles:
        subtitle_list.insert(tk.END, subtitle['text'])
    subtitle_list.pack(side=tk.RIGHT, padx=20, pady=10)

    # 绑定点击事件
    def on_click_subtitle(event):
        index = subtitle_list.curselection()
        if index:
            subtitle = subtitles[index[0]]
            on_subtitle_click(subtitle, media, progress)

    subtitle_list.bind("<ButtonRelease-1>", on_click_subtitle)

    # 播放/暂停按钮
    play_button = tk.Button(window, text="播放", command=lambda: toggle_play_pause(media, play_button))
    play_button.pack(pady=10)

    # 初始化播放器
    media = play_audio(audio_file)

    # 更新进度条和字幕
    update_progress(media, progress, label, subtitles, window)

    window.mainloop()

# 主函数
if __name__ == "__main__":
    audio_file = "D://Huawei Share//Huawei Share//bbb.m4a"  # 音频文件路径
    subtitle_file = "D://Huawei Share//Huawei Share//bbb.srt"  # 字幕文件路径
    create_gui(audio_file, subtitle_file)
