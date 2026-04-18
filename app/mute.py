# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "PySide6",
#     "pycaw",
#     "psutil",
# ]
# ///

# Solitaire Sound Guard
# Copyright (c) 2026 mizunomidori
# Licensed under the MIT License.

import sys
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QSystemTrayIcon, QMenu, QStyle)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QThread, Signal, Slot
from pycaw.pycaw import AudioUtilities

# --- ミュート処理 ---
def set_solitaire_mute(is_muted=True):
    try:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and "Solitaire" in session.Process.name():
                volume = session.SimpleAudioVolume
                volume.SetMute(1 if is_muted else 0, None)
                return True
    except Exception:
        pass
    return False

# --- バックグラウンド監視スレッド ---
class MonitorThread(QThread):
    status_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            success = set_solitaire_mute(True)
            if success:
                self.status_signal.emit("監視中: ミュートを維持しています")
            else:
                self.status_signal.emit("監視中: ソリティアの起動を待っています...")
            time.sleep(2)

    def stop(self):
        self.running = False

# --- GUI ---
class ModernMuter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solitaire Sound Guard")
        self.setFixedSize(400, 300)
        self.monitor_thread = None

        # スタイルシート
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1b26; }
            QLabel { color: #a9b1d6; font-size: 14px; font-family: 'Segoe UI', sans-serif; }
            #StatusLabel { color: #7aa2f7; font-size: 12px; }
            QPushButton {
                background-color: #24283b;
                color: #c0caf5;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                border: 1px solid #414868;
            }
            QPushButton:hover { background-color: #414868; }
            QPushButton#MuteBtn { background-color: #f7768e; color: #1a1b26; border: none; }
            QPushButton#MuteBtn:disabled { background-color: #24283b; color: #565f89; }
            QPushButton#AutoBtn { border: 2px solid #9ece6a; color: #9ece6a; }
            QPushButton#AutoBtn:checked { background-color: #9ece6a; color: #1a1b26; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Solitaire Sound Guard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #7aa2f7;")
        layout.addWidget(title)

        self.status_label = QLabel("状態: 待機中")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.mute_btn = QPushButton("今すぐミュート")
        self.mute_btn.setObjectName("MuteBtn")
        self.mute_btn.clicked.connect(self.manual_mute)
        layout.addWidget(self.mute_btn)

        self.auto_btn = QPushButton("自動監視モード")
        self.auto_btn.setObjectName("AutoBtn")
        self.auto_btn.setCheckable(True)
        self.auto_btn.clicked.connect(self.toggle_auto_mode)
        layout.addWidget(self.auto_btn)

        # --- システムトレイの設定 ---
        self.tray_icon = QSystemTrayIcon(self)
        # OS標準のアイコンをセット
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # トレイアイコンの右クリックメニュー
        tray_menu = QMenu()
        show_action = QAction("表示", self)
        show_action.triggered.connect(self.show_window)
        quit_action = QAction("終了", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        
        # アイコンクリック時の動作
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def changeEvent(self, event):
        # 最小化された時にタスクバーから隠す
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                self.hide()
                self.tray_icon.showMessage(
                    "Solitaire Sound Guard",
                    "バックグラウンドで監視を継続しています",
                    QSystemTrayIcon.Information,
                    2000
                )
        super().changeEvent(event)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # シングルクリック
            self.show_window()

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def manual_mute(self):
        if set_solitaire_mute(True):
            self.status_label.setText("状態: ミュートを適用しました")
        else:
            self.status_label.setText("状態: プロセスが見つかりません")

    def toggle_auto_mode(self):
        if self.auto_btn.isChecked():
            self.auto_btn.setText("自動監視: ON")
            self.mute_btn.setEnabled(False)
            self.monitor_thread = MonitorThread()
            self.monitor_thread.status_signal.connect(self.update_status)
            self.monitor_thread.start()
        else:
            self.auto_btn.setText("自動監視: OFF")
            self.mute_btn.setEnabled(True)
            if self.monitor_thread:
                self.monitor_thread.stop()
                self.monitor_thread.wait()
            self.status_label.setText("状態: 待機中")

    @Slot(str)
    def update_status(self, text):
        self.status_label.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 最後のウィンドウが閉じてもアプリを終了しない設定
    app.setQuitOnLastWindowClosed(False)
    
    window = ModernMuter()
    window.show()
    sys.exit(app.exec())
