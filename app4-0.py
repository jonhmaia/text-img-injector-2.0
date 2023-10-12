import os
import zipfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QFileDialog, QLabel, QWidget, QColorDialog, QFontDialog
from PyQt5 import QtWidgets, QtGui
from PIL import Image, ImageDraw, ImageFont
import PyQt5.QtGui as QImage
from PIL import ImageQt
from PyQt5.QtGui import QImage



class AddTextToImagesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Adicionar Texto às Imagens")
        self.setGeometry(100, 100, 800, 600)

        self.texts_input = QTextEdit(self)
        self.texts_input.setPlaceholderText("Lista de Textos (um por linha)")

        self.choose_directory_button = QPushButton("Selecionar Diretório", self)
        self.choose_directory_button.clicked.connect(self.choose_directory)

        self.choose_color_button = QPushButton("Escolher Cor do Texto", self)
        self.choose_color_button.clicked.connect(self.choose_color)

        self.text_position_label = QLabel("Posição do Texto (x, y):", self)
        self.text_position_input = QTextEdit(self)
        self.text_position_input.setPlaceholderText("Coordenadas x, y")

        self.text_size_label = QLabel("Tamanho da Fonte:", self)
        self.text_size_input = QTextEdit(self)
        self.text_size_input.setPlaceholderText("Tamanho da fonte")

        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)

        self.execute_button = QPushButton("Executar", self)
        self.execute_button.clicked.connect(self.execute)

        self.result_label = QLabel(self)

        layout = QVBoxLayout()
        layout.addWidget(self.texts_input)
        layout.addWidget(self.choose_directory_button)
        layout.addWidget(self.choose_color_button)
        layout.addWidget(self.image_label)
        layout.addWidget(self.text_position_label)
        layout.addWidget(self.text_position_input)
        layout.addWidget(self.text_size_label)
        layout.addWidget(self.text_size_input)
        layout.addWidget(self.execute_button)
        layout.addWidget(self.result_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        #  caminho para o arquivo TTF da fonte Tahoma
        self.tahoma_font_path = "TAHOMABD.TTF"

        # Definindo a fonte padrão como Tahoma
        self.selected_font = ImageFont.truetype(self.tahoma_font_path, 20)
        self.selected_text_color = (0, 0, 0)

        self.selected_directory = None
        self.selected_image = None
        self.selected_image_path = None

    def choose_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Diretório", options=options)
        if directory:
            self.selected_directory = directory
            self.update_image_label()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_text_color = (color.red(), color.green(), color.blue())

    def update_image_label(self):
        if self.selected_directory:
            image_files = [file for file in os.listdir(self.selected_directory) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            if image_files:
                first_image_path = os.path.join(self.selected_directory, image_files[0])
                self.selected_image = Image.open(first_image_path)
                self.selected_image_path = first_image_path
                max_width = 400
                max_height = 300
                self.selected_image.thumbnail((max_width, max_height), Image.LANCZOS)
            else:
                self.selected_image = None
                self.selected_image_path = None
            self.display_image()

    def execute(self):
        if self.selected_directory and self.selected_image:
            textos = self.texts_input.toPlainText().split('\n')

            if len(textos) == 0:
                self.result_label.setText("Nenhum texto fornecido.")
                return

            x, y = map(int, self.text_position_input.toPlainText().split(','))
            font_size = int(self.text_size_input.toPlainText())

            temp_directory = "imagens_com_texto"
            os.makedirs(temp_directory, exist_ok=True)

            for nome_imagem in os.listdir(self.selected_directory):
                imagem = Image.open(os.path.join(self.selected_directory, nome_imagem))
                draw = ImageDraw.Draw(imagem)

                if len(textos) > 0:
                    texto = textos.pop(0)
                    selected_font = ImageFont.truetype(self.tahoma_font_path, font_size)
                    draw.text((x, y), texto, fill=self.selected_text_color, font=selected_font)

                imagem.save(os.path.join(temp_directory, nome_imagem))

            self.update_image_label()

            with zipfile.ZipFile("imagens_com_texto.zip", "w") as zipf:
                for root, dirs, files in os.walk(temp_directory):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), temp_directory))

            self.result_label.setText("Textos adicionados às imagens com sucesso.")

    def display_image(self):
        if self.selected_image:
            q_image = QtGui.QImage(self.selected_image.tobytes(), self.selected_image.width, self.selected_image.height, self.selected_image.width * 4, QtGui.QImage.Format_RGBA8888)
            pixmap = QtGui.QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication([])
    window = AddTextToImagesApp()
    window.show()
    app.exec()