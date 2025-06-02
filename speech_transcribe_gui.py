import sys
import os
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import logging
from speech_transcribe_script import VoiceProcessor
from logging_config import setup_logging

# 로깅 설정 초기화
setup_logging()
logger = logging.getLogger(__name__)

class TextHandler(logging.Handler):
    """로그 메시지를 GUI 텍스트 위젯에 출력하는 핸들러"""
    def __init__(self, widget: scrolledtext.ScrolledText):
        super().__init__()
        self.widget = widget

        root_logger = logging.getLogger()
        if root_logger.handlers:
            self.setFormatter(root_logger.handlers[0].formatter)

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, msg + '\n')
        self.widget.configure(state='disabled')
        self.widget.yview(tk.END)

class VoiceGUI:
    """음성 인식 GUI 애플리케이션"""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Speech Transcribe GUI")
        self.root.geometry("400x500")
        self.processor: Optional[VoiceProcessor] = None
        self.thread: Optional[threading.Thread] = None
        self.is_running: bool = False
        self._init_ui()
        self._setup_logger()

    def _init_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        style = ttk.Style()
        style.configure("Control.TButton", padding=5)
        self.start_btn = ttk.Button(
            btn_frame, text="시작", command=self.start, style="Control.TButton"
        )
        self.stop_btn = ttk.Button(
            btn_frame, text="정지", command=self.stop, state=tk.DISABLED, style="Control.TButton"
        )
        self.exit_btn = ttk.Button(
            btn_frame, text="종료", command=self.exit, style="Control.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.exit_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.log_area = scrolledtext.ScrolledText(
            main_frame, height=15, state='disabled', wrap=tk.WORD
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.tag_configure('log', foreground='gray', font=('맑은 고딕', 9))

    def _setup_logger(self) -> None:
        handler = TextHandler(self.log_area)
        logging.getLogger().addHandler(handler)

    def _update_button_states(self, is_running: bool) -> None:
        self.start_btn.configure(state=tk.DISABLED if is_running else tk.NORMAL)
        self.stop_btn.configure(state=tk.NORMAL if is_running else tk.DISABLED)

    def start(self) -> None:
        if not self.is_running:
            self.processor = VoiceProcessor()
            self.thread = threading.Thread(target=self.processor.start, daemon=True)
            self.thread.start()
            self.is_running = True
            self._update_button_states(True)

    def stop(self) -> None:
        if self.is_running and self.processor:
            self.processor.stop()
            self.is_running = False
            self._update_button_states(False)

    def exit(self) -> None:
        self.processor.exit()
        self.root.quit()

def main() -> None:
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    root = tk.Tk()
    app = VoiceGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
