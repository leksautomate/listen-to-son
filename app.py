import sys
import subprocess
from faster_whisper import WhisperModel
import yt_dlp
import logging
from moviepy.editor import *
from moviepy.video.fx.freeze import freeze
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLineEdit, QComboBox, QColorDialog, QSpinBox, QTextEdit, QProgressBar, QGridLayout
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class VideoEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TikTok Freeze + Subtitle Tool")
        self.resize(600, 700)

        # Inputs and controls
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter TikTok URL here...")
        self.file_label = QLabel("No video selected.")
        self.select_file_btn = QPushButton("Select MP4")
        self.mode_select = QComboBox()
        self.mode_select.addItems(["line_by_line", "karaoke"])

        self.font_size_input = QSpinBox()
        self.font_size_input.setValue(120)
        self.font_size_input.setRange(10, 200)

        self.word_limit_input = QSpinBox()
        self.word_limit_input.setValue(2)
        self.word_limit_input.setRange(1, 20)

        self.word_color_btn = QPushButton("Word Color")
        self.highlight_color_btn = QPushButton("Highlight Color")
        self.outline_color_btn = QPushButton("Outline Color")

        self.run_btn = QPushButton("Run")
        self.preview_btn = QPushButton("Preview Output")
        self.preview_btn.setEnabled(False)
        self.output_filename = "output/final_output.mp4"

        self.progress = QProgressBar()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        # Colors
        self.word_color = "white"
        self.highlight_color = "yellow"
        self.outline_color = "black"
        self.selected_video = None

        self.setup_logging()
        self.apply_stylesheet()
        self.build_ui()
        self.connect_ui()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                color: #D8DEE9;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4C566A;
                border: 1px solid #5E81AC;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QPushButton:pressed {
                background-color: #81A1C1;
            }
            QPushButton:disabled {
                background-color: #3B4252;
                color: #4C566A;
                border-color: #4C566A;
            }
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                padding: 5px;
                border-radius: 4px;
            }
            QLabel {
                padding-left: 2px;
            }
            QProgressBar {
                border: 1px solid #4C566A;
                border-radius: 4px;
                text-align: center;
                color: #ECEFF4;
            }
            QProgressBar::chunk {
                background-color: #88C0D0;
                border-radius: 4px;
            }
            QTextEdit {
                font-family: Consolas, Courier, monospace;
            }
        """)

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # --- Input Group ---
        input_group_layout = QVBoxLayout()
        input_group_layout.addWidget(QLabel("TikTok URL:"))
        input_group_layout.addWidget(self.url_input)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.select_file_btn, 1)
        file_layout.addWidget(self.file_label, 2)
        input_group_layout.addLayout(file_layout)
        main_layout.addLayout(input_group_layout)

        # --- Settings Group ---
        settings_layout = QGridLayout()
        settings_layout.setSpacing(10)
        settings_layout.addWidget(QLabel("Subtitle Mode:"), 0, 0)
        settings_layout.addWidget(self.mode_select, 0, 1)
        settings_layout.addWidget(QLabel("Font Size:"), 1, 0)
        settings_layout.addWidget(self.font_size_input, 1, 1)
        settings_layout.addWidget(QLabel("Max Words per Line:"), 2, 0)
        settings_layout.addWidget(self.word_limit_input, 2, 1)
        main_layout.addLayout(settings_layout)

        # --- Color Group ---
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.word_color_btn)
        color_layout.addWidget(self.highlight_color_btn)
        color_layout.addWidget(self.outline_color_btn)
        main_layout.addLayout(color_layout)

        # --- Action Group ---
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.run_btn, 1)
        action_layout.addWidget(self.preview_btn, 1)
        main_layout.addLayout(action_layout)

        # --- Progress and Log ---
        main_layout.addWidget(QLabel("Progress:"))
        main_layout.addWidget(self.progress)
        main_layout.addWidget(QLabel("Log:"))
        main_layout.addWidget(self.log_box, 1)

    def connect_ui(self):
        self.select_file_btn.clicked.connect(self.select_mp4)
        self.word_color_btn.clicked.connect(lambda: self.pick_color("word"))
        self.highlight_color_btn.clicked.connect(lambda: self.pick_color("highlight"))
        self.outline_color_btn.clicked.connect(lambda: self.pick_color("outline"))
        self.run_btn.clicked.connect(self.process_video)
        self.preview_btn.clicked.connect(self.preview_video)

    def setup_logging(self):
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(level=logging.INFO, format=log_format)
        # Add a stream handler to also print to console
        root_logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(handler)

    def log(self, text):
        logging.info(text)
        self.log_box.append(text)
        QApplication.processEvents()

    def pick_color(self, kind):
        color = QColorDialog.getColor(QColor(getattr(self, f"{kind}_color")))
        if color.isValid():
            setattr(self, f"{kind}_color", color.name())
            self.log(f"🎨 {kind.capitalize()} color set to {color.name()}")

    def select_mp4(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select MP4", "", "Videos (*.mp4)")
        if file:
            self.selected_video = file
            self.file_label.setText(file.split('/')[-1])
            self.log(f"📹 Video selected: {file}")

    def preview_video(self):
        try:
            subprocess.Popen(["start", self.output_filename], shell=True)
        except Exception as e:
            self.log(f"❌ Error previewing video: {e}")



    def group_words(self, words, max_words):
        lines = []
        current_line = []
        for w in words:
            current_line.append(w)
            if len(current_line) >= max_words or (w['word'].strip().endswith(('.', '?', '!')) and len(current_line) > 1) or w == words[-1]:
                if current_line:
                    lines.append(current_line)
                current_line = []
        if current_line:
            lines.append(current_line)
        return lines

    def process_video(self):
        if not self.selected_video or not self.url_input.text().strip():
            self.log("❌ Missing TikTok URL or video file.")
            return

        self.run_btn.setEnabled(False)
        self.progress.setValue(5)
        self.log("🎧 Downloading TikTok audio...")
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'tiktok_audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'socket_timeout': 30,
                'retries': 3
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url_input.text().strip()])
            mp3 = AudioFileClip("tiktok_audio.mp3")
        except Exception as e:
            self.log(f"❌ Audio download failed: {e}")
            self.run_btn.setEnabled(True)
            return

        self.progress.setValue(15)
        self.log("🎬 Loading MP4...")
        video = VideoFileClip(self.selected_video)
        freeze_start = video.duration - 2
        freeze_clip = freeze(video.subclip(freeze_start), t=0, freeze_duration=mp3.duration)
        
        full_video = concatenate_videoclips([video.subclip(0, freeze_start), freeze_clip])
        
        combined_audio = concatenate_audioclips([video.audio.subclip(0, freeze_start), mp3])
        full_video = full_video.set_audio(combined_audio)

        self.progress.setValue(40)
        self.log("🧠 Transcribing with faster-whisper...")
        self.log("🧠 Transcribing main video audio...")
        main_audio_path = "main_audio.mp3"
        video.audio.subclip(0, freeze_start).write_audiofile(main_audio_path, codec='mp3')
        model = WhisperModel("base", device="cpu", compute_type="int8")
        main_segments, _ = model.transcribe(main_audio_path, word_timestamps=True)
        main_words = []
        for segment in main_segments:
            for word in segment.words:
                main_words.append(word._asdict())

        self.log("🧠 Transcribing frozen part audio...")
        segments, _ = model.transcribe("tiktok_audio.mp3", word_timestamps=True)
        words = []
        for segment in segments:
            for word in segment.words:
                words.append(word._asdict())

        # Create dynamic filename
        first_three_words = "-".join([w['word'].strip() for w in words[:3]]).upper()
        self.output_filename = f"output/{first_three_words}.mp4"
        self.log(f"📝 Output filename will be: {self.output_filename}")

        self.progress.setValue(60)
        self.log("📝 Generating subtitles...")
        subs = []
        mode = self.mode_select.currentText()
        fontsize = self.font_size_input.value()
        max_words = self.word_limit_input.value()

        main_lines = self.group_words(main_words, max_words)
        frozen_lines = self.group_words(words, max_words)

        if mode == "line_by_line":
            # Subtitles for main part
            for line in main_lines:
                line_text = " ".join([w['word'] for w in line]).upper()
                start_time = line[0]['start']
                end_time = line[-1]['end']
                txt = TextClip(line_text, fontsize=fontsize, font="Arial-Bold", color=self.word_color,
                               stroke_color=self.outline_color, stroke_width=2, method='caption', align='center', size=(video.w*0.9, None))
                txt = txt.set_start(start_time).set_duration(end_time - start_time).set_position("center")
                subs.append(txt)

            # Subtitles for frozen part
            for line in frozen_lines:
                line_text = " ".join([w['word'] for w in line]).upper()
                start_time = line[0]['start']
                end_time = line[-1]['end']
                txt = TextClip(line_text, fontsize=fontsize, font="Arial-Bold", color=self.word_color,
                               stroke_color=self.outline_color, stroke_width=2, method='caption', align='center', size=(video.w*0.9, None))
                txt = txt.set_start(start_time + freeze_start).set_duration(end_time - start_time).set_position("center")
                subs.append(txt)
        else: # Karaoke mode
            # Karaoke for main part
            for line_words in main_lines:
                line_start_time = line_words[0]['start']
                for i, w in enumerate(line_words):
                    word_text = w['word'].upper()
                    word_start_time = w['start']
                    word_end_time = w['end']
                    
                    # Background text (whole line)
                    background_text = " ".join([lw['word'] for lw in line_words]).upper()
                    bg_txt_clip = TextClip(background_text, fontsize=fontsize, font="Arial-Bold", color=self.word_color, stroke_color=self.outline_color, stroke_width=2, method='caption', align='center', size=(video.w*0.9, None))
                    bg_txt_clip = bg_txt_clip.set_start(line_start_time).set_duration(line_words[-1]['end'] - line_start_time).set_position("center")
                    subs.append(bg_txt_clip)

                    # Highlighted text (word by word)
                    highlight_txt_clip = TextClip(word_text, fontsize=fontsize, font="Arial-Bold", color=self.highlight_color, stroke_color=self.outline_color, stroke_width=2, method='caption', align='center', size=(video.w*0.9, None))
                    highlight_txt_clip = highlight_txt_clip.set_start(word_start_time).set_duration(word_end_time - word_start_time).set_position("center")
                    subs.append(highlight_txt_clip)

            # Karaoke for frozen part
            for line_words in frozen_lines:
                line_start_time = line_words[0]['start'] + freeze_start
                for i, w in enumerate(line_words):
                    word_text = w['word'].upper()
                    word_start_time = w['start'] + freeze_start
                    word_end_time = w['end'] + freeze_start

                    background_text = " ".join([lw['word'] for lw in line_words]).upper()
                    bg_txt_clip = TextClip(background_text, fontsize=fontsize, font="Arial-Bold", color=self.word_color, stroke_color=self.outline_color, stroke_width=2, method='caption', align='center', size=(video.w*0.9, None))
                    bg_txt_clip = bg_txt_clip.set_start(line_start_time).set_duration((line_words[-1]['end'] + freeze_start) - line_start_time).set_position("center")
                    subs.append(bg_txt_clip)

                    highlight_txt_clip = TextClip(word_text, fontsize=fontsize, font="Arial-Bold", color=self.highlight_color, stroke_color=self.outline_color, stroke_width=2, method='caption', align='center', size=(video.w*0.9, None))
                    highlight_txt_clip = highlight_txt_clip.set_start(word_start_time).set_duration(word_end_time - word_start_time).set_position("center")
                    subs.append(highlight_txt_clip)

        self.progress.setValue(80)
        self.log("💾 Exporting final video...")
        final = CompositeVideoClip([full_video] + subs)
        final.write_videofile(self.output_filename, codec="libx264", audio_codec="aac", threads=4, logger='bar')
        
        # Clean up temporary files
        import os
        try:
            if os.path.exists("main_audio.mp3"):
                os.remove("main_audio.mp3")
                self.log("🧹 Cleaned up main_audio.mp3")
            if os.path.exists("tiktok_audio.mp3"):
                os.remove("tiktok_audio.mp3")
                self.log("🧹 Cleaned up tiktok_audio.mp3")
        except Exception as e:
            self.log(f"⚠️ Warning: Could not clean up temporary files: {e}")
        
        self.progress.setValue(100)
        self.preview_btn.setEnabled(True)
        self.run_btn.setEnabled(True)
        self.log(f"✅ Done! Saved as {self.output_filename}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VideoEditorApp()
    win.show()
    sys.exit(app.exec())
