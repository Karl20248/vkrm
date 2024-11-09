import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import subprocess
import numpy as np

class VideoStream(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Stream")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.process = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)

        self.resolution = (640, 480)  # Начальное разрешение
        self.rtsp_url = ""  # Изначально пустой RTSP URL

    def start_stream(self, rtsp_url):
        self.rtsp_url = rtsp_url  # Сохраняем текущий RTSP URL
        command = [
            'ffmpeg',
            '-i', self.rtsp_url,
            '-f', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-'
        ]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Проверка ошибок
        stderr_output = self.process.stderr.read()
        if stderr_output:
            print(stderr_output.decode())
            return False
        return True

    def update_frame(self):
        if self.process is not None:
            raw_frame = self.process.stdout.read(self.resolution[0] * self.resolution[1] * 3)
            if len(raw_frame) == self.resolution[0] * self.resolution[1] * 3:
                image = QImage(np.frombuffer(raw_frame, np.uint8).reshape((self.resolution[1], self.resolution[0], 3)), self.resolution[0], self.resolution[1], QImage.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        if self.process:
            self.process.terminate()
        event.accept()

    def set_resolution(self, resolution):
        if self.process:
            self.process.terminate()
        self.resolution = resolution
        # Запускаем поток с текущим RTSP URL
        if self.rtsp_url:
            self.start_stream(self.rtsp_url)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KSO_klient")
        self.setGeometry(100, 100, 800, 600)

        # Создание текстового поля для ввода RTSP URL
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Введите RTSP URL")
        self.url_input.setFixedWidth(300)  # Устанавливаем фиксированную ширину текстового поля

        # Создание кнопки для запуска потока
        self.start_button = QPushButton("Запустить", self)
        self.start_button.setFixedWidth(100)  # Устанавливаем фиксированную ширину кнопки
        self.start_button.setFixedHeight(30)  # Устанавливаем фиксированную высоту кнопки
        self.start_button.clicked.connect(self.start_video_stream)

        # Создание верхней панели
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.url_input)
        top_layout.addWidget(self.start_button)

        # Создание виджета для потока
        self.video_stream = VideoStream()

        # Создание выпадающего списка для выбора разрешения
        self.resolution_selector = QComboBox(self)
        self.resolution_selector.addItems(["240p", "360p", "480p", "720p"])
        self.resolution_selector.setFixedWidth(100)  # Устанавливаем фиксированную ширину для combobox
        self.resolution_selector.currentTextChanged.connect(self.change_resolution)

        # Создание основного layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)  # Добавляем верхнюю панель с текстовым полем и кнопкой
        main_layout.addWidget(self.video_stream)  # Добавляем виджет для потока

        # Создаем отдельный layout для combobox и добавляем его в верхний правый угол
        combo_layout = QHBoxLayout()
        combo_layout.addStretch()  # Добавляем растяжение для выравнивания по правому краю
        combo_layout.addWidget(self.resolution_selector)  # Добавляем combobox
        main_layout.addLayout(combo_layout)  # Добавляем layout с combobox в основной layout

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def start_video_stream(self):
        rtsp_url = self.url_input.text()
        if self.video_stream.start_stream(rtsp_url):
            QMessageBox.information(self, "Успех", "Поток запущен.")
        else:
            QMessageBox.warning(self, "Ошибка", "Данный URL не найден, попробуйте ввести другой.")

    def change_resolution(self, resolution):
        if resolution == "240p":
            self.video_stream.set_resolution((426, 240))
        elif resolution == "360p":
            self.video_stream.set_resolution((640, 360))
        elif resolution == "480p":
            self.video_stream.set_resolution((640, 480))
        elif resolution == "720p":
            self.video_stream.set_resolution((1280, 720))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())