import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, 
                             QMessageBox, QFormLayout, QFileDialog, QComboBox)
from PyQt5.QtCore import QSize
import csv
import webbrowser

# Lista global de fics
fics = []
ARCHIVO_CSV = "fics.csv"

def cargar_fics_csv():
    fics.clear()
    try:
        with open(ARCHIVO_CSV, mode='r', newline='') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                fics.append(row)
    except FileNotFoundError:
        pass

def guardar_fics_csv():
    with open(ARCHIVO_CSV, mode='w', newline='') as file:
        fieldnames = ['nombre', 'autor', 'fandom', 'tags', 'ruta']
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for fic in fics:
            writer.writerow(fic)

class PantallaInicio(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setMinimumSize(QSize(320, 400))

    def initUI(self):
        self.setStyleSheet("background-color: #ebe0f8;")
        layout = QVBoxLayout()
        
        self.lista_fics = QListWidget()
        self.actualizar_lista()
        self.lista_fics.itemDoubleClicked.connect(self.abrir_fic)

        btn_nuevo = QPushButton('Introducir nuevo')
        btn_ordenar = QPushButton('Ordenar por categoría')
        btn_buscar = QPushButton('Buscar fic')
        
        btn_nuevo.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #B79CED; color: white;")
        btn_ordenar.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #957FEF; color: white;")
        btn_buscar.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #7161EF; color: white;")

        self.lista_fics.setStyleSheet("font-family: 'Calibri'; font-size: 15px; background-color: #f5effd")

        btn_nuevo.clicked.connect(self.mostrar_pantalla_nuevo)
        btn_ordenar.clicked.connect(self.mostrar_pantalla_ordenar)
        btn_buscar.clicked.connect(self.mostrar_pantalla_buscar)
        
        layout.addWidget(QLabel('Lista de fics:'))
        layout.addWidget(self.lista_fics)
        layout.addWidget(btn_nuevo)
        layout.addWidget(btn_ordenar)
        layout.addWidget(btn_buscar)

        self.setLayout(layout)
        self.setWindowTitle('Inicio')

    def actualizar_lista(self):
        self.lista_fics.clear()
        for fic in fics:
            self.lista_fics.addItem(f"{fic['nombre']} - {fic['autor']} - {fic['fandom']} - {fic['tags']}")

    def abrir_fic(self, item):
        index = self.lista_fics.row(item)
        if 0 <= index < len(fics):
            ruta = fics[index]['ruta']
            try:
                webbrowser.open(ruta)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def mostrar_pantalla_nuevo(self):
        self.nuevo_fic = PantallaNuevoFic(self)
        self.nuevo_fic.show()

    def mostrar_pantalla_ordenar(self):
        self.ordenar_fics = PantallaOrdenar(self)
        self.ordenar_fics.show()

    def mostrar_pantalla_buscar(self):
        self.buscar_fics = PantallaBuscar(self)
        self.buscar_fics.show()

class PantallaNuevoFic(QWidget):
    def __init__(self, pantalla_inicio):
        super().__init__()
        self.pantalla_inicio = pantalla_inicio
        self.initUI()
        self.setMinimumSize(QSize(320, 210))

    def initUI(self):
        self.setStyleSheet("background-color: #ebe0f8;")
        formLayout = QFormLayout(self)
        
        self.nombre_input = QLineEdit()
        self.autor_input = QLineEdit()
        self.fandom_input = QLineEdit()
        self.tag_input = QLineEdit()
        self.ruta_input = QLineEdit()

        text_input_style = "font-family: 'Calibri'; font-size: 14px; color: #333; background-color: #f5f5f5; padding: 5px;"
        for field in [self.nombre_input, self.autor_input, self.fandom_input, self.tag_input, self.ruta_input]:
            field.setStyleSheet(text_input_style)

        btn_seleccionar_ruta = QPushButton('Seleccionar archivo')
        btn_seleccionar_ruta.clicked.connect(self.seleccionar_archivo)
        btn_guardar = QPushButton('Guardar')
        btn_guardar.clicked.connect(self.guardar_fic)
        
        formLayout.addRow(QLabel('Nombre: '), self.nombre_input)
        formLayout.addRow(QLabel('Autor: '), self.autor_input)
        formLayout.addRow(QLabel('Fandom: '), self.fandom_input)  # Cambié "Rating" a "Fandom"
        formLayout.addRow(QLabel('Tags:'), self.tag_input)
        formLayout.addRow(QLabel('Ruta del fic:'), self.ruta_input)
        formLayout.addRow(btn_seleccionar_ruta, btn_guardar)

        # Estilo para las etiquetas
        label_style = """font-family: 'Calibri'; font-size: 14px; font-weight: bold; color: #334; """
        for i in range(formLayout.rowCount() - 1):  # Excluye el último row de botones
            label = formLayout.itemAt(i, QFormLayout.LabelRole).widget()
            label.setStyleSheet(label_style)

        # Estilo para los botones
        btn_style = """ font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #B79CED; color: white; padding: 8px 15px;"""
        btn_seleccionar_ruta.setStyleSheet(btn_style)
        btn_guardar.setStyleSheet(btn_style)

        self.setLayout(formLayout)
        self.setWindowTitle('Introducir nuevo fic')

    def seleccionar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, 'Seleccionar archivo', '', 'Todos los archivos (*)')
        if ruta:
            self.ruta_input.setText(ruta)

    def guardar_fic(self):
        nombre = self.nombre_input.text()
        autor = self.autor_input.text()
        fandom = self.fandom_input.text()
        tags = self.tag_input.text()
        ruta = self.ruta_input.text()

        if nombre and autor and fandom and ruta:  # Verifica que los campos necesarios estén completos
            fic = {'nombre': nombre, 'autor': autor, 'fandom': fandom, 'tags': tags, 'ruta': ruta}
            fics.append(fic)
            guardar_fics_csv()
            self.pantalla_inicio.actualizar_lista()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Por favor, rellena todos los campos.')

class PantallaOrdenar(QWidget):
    def __init__(self, pantalla_inicio):
        super().__init__()
        self.pantalla_inicio = pantalla_inicio
        self.initUI()
        self.setMinimumSize(QSize(200, 80))

    def initUI(self):
        layout = QVBoxLayout()
        
        self.combo_ordenar = QComboBox()
        self.combo_ordenar.addItems(["Alfabéticamente", "Por tag", "Por autor", "Por fandom"])
        self.combo_ordenar.setStyleSheet("font-family: 'Calibri'; font-size: 14px; color: #333; background-color: #f5f5f5; padding: 5px;")
        
        btn_ordenar = QPushButton('Ordenar')
        btn_ordenar.clicked.connect(self.ordenar)
        btn_ordenar.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #B79CED; color: white;")
        
        layout.addWidget(self.combo_ordenar)
        layout.addWidget(btn_ordenar)
        
        self.setLayout(layout)
        self.setWindowTitle('Ordenar fics')

    def ordenar(self):
        criterio = self.combo_ordenar.currentText()
        if criterio == 'Alfabéticamente':
            fics.sort(key=lambda x: x['nombre'].lower())  
        elif criterio == 'Por tag':
            fics.sort(key=lambda x: x['tags'].lower())  
        elif criterio == 'Por autor':
            fics.sort(key=lambda x: x['autor'].lower())  
        elif criterio == 'Por fandom':
            fics.sort(key=lambda x: x['fandom'].lower())
        guardar_fics_csv()
        self.pantalla_inicio.actualizar_lista()
        self.close()

class PantallaBuscar(QWidget):
    def __init__(self, pantalla_inicio):
        super().__init__()
        self.pantalla_inicio = pantalla_inicio
        self.initUI()
        self.setMinimumSize(QSize(320, 180))

    def initUI(self):
        self.setStyleSheet("background-color: #ebe0f8;")
        formLayout = QFormLayout(self)

        self.nombre_input = QLineEdit()  
        self.autor_input = QLineEdit()    
        self.tag_input = QLineEdit()     
        self.fandom_input = QLineEdit()   

        text_input_style = "font-family: 'Calibri'; font-size: 14px; color: #333; background-color: #f5f5f5; padding: 5px;"
        # Aplica el estilo a todos los campos de entrada
        self.nombre_input.setStyleSheet(text_input_style)
        self.autor_input.setStyleSheet(text_input_style)
        self.tag_input.setStyleSheet(text_input_style)
        self.fandom_input.setStyleSheet(text_input_style)

        btn_buscar = QPushButton('Buscar')
        btn_buscar.clicked.connect(self.buscar)  # Conecta el botón a la función buscar
        btn_buscar.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #B79CED; color: white;")

        # Agrega los campos de entrada y el botón al layout
        formLayout.addRow(QLabel('Nombre:'), self.nombre_input)
        formLayout.addRow(QLabel('Autor:'), self.autor_input)
        formLayout.addRow(QLabel('Tag:'), self.tag_input)
        formLayout.addRow(QLabel('Fandom:'), self.fandom_input)  # Asegúrate de que el QLabel corresponda con el campo correcto
        formLayout.addRow(btn_buscar)

        # Estilo para las etiquetas
        label_style = """font-family: 'Calibri'; font-size: 14px; font-weight: bold; color: #334; """
        for i in range(formLayout.rowCount() - 1):  # Excluye el último row de botones
            label = formLayout.itemAt(i, QFormLayout.LabelRole).widget()
            label.setStyleSheet(label_style)

        # Estilo para los botones
        btn_style = """ font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #B79CED; color: white; padding: 8px 15px;"""
        btn_buscar.setStyleSheet(btn_style)

        self.setLayout(formLayout)
        self.setWindowTitle('Buscar fic')

    def buscar(self):
        # Captura el texto de todos los campos de entrada
        nombre = self.nombre_input.text().lower()
        autor = self.autor_input.text().lower()
        tag = self.tag_input.text().lower()
        fandom = self.fandom_input.text().lower() 

        # Filtra los resultados según los criterios de búsqueda
        resultados = [fic for fic in fics if (nombre in fic['nombre'].lower() or nombre == "") and 
                     (autor in fic['autor'].lower() or autor == "") and 
                     (tag in fic['tags'].lower() or tag == "") and 
                     (fandom in fic['fandom'].lower() or fandom == "")]  # Agrega la condición de fandom

        if resultados:
            self.pantalla_inicio.lista_fics.clear()
            for fic in resultados:
                self.pantalla_inicio.lista_fics.addItem(f"{fic['nombre']} - {fic['autor']} - {fic['fandom']} - {fic['tags']}")
            self.close()
        else:
            QMessageBox.information(self, 'Sin resultados', 'No se encontró ningún fic con los criterios dados.')

if __name__ == '__main__':
    cargar_fics_csv()
    app = QApplication(sys.argv)
    pantalla_inicio = PantallaInicio()
    pantalla_inicio.show()
    sys.exit(app.exec_())


