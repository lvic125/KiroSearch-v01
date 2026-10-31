import sys
import csv
import webbrowser
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget,
                             QMessageBox, QFormLayout, QFileDialog, QComboBox)
from PyQt5.QtCore import QSize

# Global list of fics. Every fic is a dict with the keys in FIELDNAMES.
fics = []
CSV_FILE = "fics.csv"
FIELDNAMES = ['name', 'author', 'fandom', 'tags', 'route']


def load_fics_csv():
    fics.clear()
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # Make sure every key exists, even if the CSV is missing a column
                fics.append({key: row.get(key) or '' for key in FIELDNAMES})
    except FileNotFoundError:
        pass


def save_fics_csv():
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES, delimiter=';')
        writer.writeheader()
        for fic in fics:
            writer.writerow(fic)


def fic_label(fic):
    return f"{fic['name']} - {fic['author']} - {fic['fandom']} - {fic['tags']}"


LABEL_STYLE = "font-family: 'Calibri'; font-size: 14px; font-weight: bold; color: #334;"
INPUT_STYLE = "font-family: 'Calibri'; font-size: 14px; color: #333; background-color: #f5f5f5; padding: 5px;"
BTN_STYLE = ("font-family: 'Calibri'; font-size: 16px; font-weight: bold; "
             "background-color: #B79CED; color: white; padding: 8px 15px;")


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.shown_fics = []  # the fics currently displayed (all of them, or search results)
        self.initUI()
        self.setMinimumSize(QSize(320, 400))

    def initUI(self):
        self.setStyleSheet("background-color: #ebe0f8;")
        layout = QVBoxLayout()

        self.fic_list = QListWidget()
        self.refresh_list()
        self.fic_list.itemDoubleClicked.connect(self.open_fic)

        btn_new = QPushButton('Add new fic')
        btn_sort = QPushButton('Sort by category')
        btn_search = QPushButton('Search fic')

        btn_new.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #B79CED; color: white;")
        btn_sort.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #957FEF; color: white;")
        btn_search.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #7161EF; color: white;")

        self.fic_list.setStyleSheet("font-family: 'Calibri'; font-size: 15px; background-color: #f5effd")

        btn_new.clicked.connect(self.show_new_screen)
        btn_sort.clicked.connect(self.show_sort_screen)
        btn_search.clicked.connect(self.show_search_screen)

        layout.addWidget(QLabel('Fanfic list:'))
        layout.addWidget(self.fic_list)
        layout.addWidget(btn_new)
        layout.addWidget(btn_sort)
        layout.addWidget(btn_search)

        self.setLayout(layout)
        self.setWindowTitle('Home')

    def refresh_list(self, results=None):
        """Show all fics, or only `results` (e.g. from a search)."""
        self.shown_fics = list(fics) if results is None else list(results)
        self.fic_list.clear()
        for fic in self.shown_fics:
            self.fic_list.addItem(fic_label(fic))

    def open_fic(self, item):
        # Use the displayed list, so double-click opens the right fic after a search too
        index = self.fic_list.row(item)
        if 0 <= index < len(self.shown_fics):
            route = self.shown_fics[index]['route']
            try:
                webbrowser.open(route)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Couldn't open file: {str(e)}")

    def show_new_screen(self):
        self.new_fic = NewFicScreen(self)
        self.new_fic.show()

    def show_sort_screen(self):
        self.sort_fics = SortScreen(self)
        self.sort_fics.show()

    def show_search_screen(self):
        self.search_fics = SearchScreen(self)
        self.search_fics.show()


class NewFicScreen(QWidget):
    def __init__(self, home_screen):
        super().__init__()
        self.home_screen = home_screen
        self.initUI()
        self.setMinimumSize(QSize(320, 210))

    def initUI(self):
        self.setStyleSheet("background-color: #ebe0f8;")
        form_layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.author_input = QLineEdit()
        self.fandom_input = QLineEdit()
        self.tag_input = QLineEdit()
        self.route_input = QLineEdit()

        for field in [self.name_input, self.author_input, self.fandom_input, self.tag_input, self.route_input]:
            field.setStyleSheet(INPUT_STYLE)

        btn_select_route = QPushButton('Select file')
        btn_select_route.clicked.connect(self.select_file)
        btn_save = QPushButton('Save')
        btn_save.clicked.connect(self.save_fic)

        form_layout.addRow(QLabel('Name: '), self.name_input)
        form_layout.addRow(QLabel('Author: '), self.author_input)
        form_layout.addRow(QLabel('Fandom: '), self.fandom_input)
        form_layout.addRow(QLabel('Tags:'), self.tag_input)
        form_layout.addRow(QLabel('Fic route:'), self.route_input)
        form_layout.addRow(btn_select_route, btn_save)

        # Style for the labels (skips the last row, which holds the buttons)
        for i in range(form_layout.rowCount() - 1):
            label = form_layout.itemAt(i, QFormLayout.LabelRole).widget()
            label.setStyleSheet(LABEL_STYLE)

        btn_select_route.setStyleSheet(BTN_STYLE)
        btn_save.setStyleSheet(BTN_STYLE)

        self.setLayout(form_layout)
        self.setWindowTitle('Add new fic')

    def select_file(self):
        route, _ = QFileDialog.getOpenFileName(self, 'Select file', '', 'All files (*)')
        if route:
            self.route_input.setText(route)

    def save_fic(self):
        name = self.name_input.text().strip()
        author = self.author_input.text().strip()
        fandom = self.fandom_input.text().strip()
        tags = self.tag_input.text().strip()
        route = self.route_input.text().strip()

        if name and author and fandom and route:  # Tags are optional
            fics.append({'name': name, 'author': author, 'fandom': fandom, 'tags': tags, 'route': route})
            save_fics_csv()
            self.home_screen.refresh_list()
            self.close()
        else:
            QMessageBox.warning(self, 'ERROR', 'Please fill in all the fields')


class SortScreen(QWidget):
    # Dropdown text -> key in the fic dict
    SORT_OPTIONS = {
        "Sort by name": 'name',
        "Sort by tag": 'tags',
        "Sort by author": 'author',
        "Sort by fandom": 'fandom',
    }

    def __init__(self, home_screen):
        super().__init__()
        self.home_screen = home_screen
        self.initUI()
        self.setMinimumSize(QSize(200, 80))

    def initUI(self):
        layout = QVBoxLayout()

        self.combo_sort = QComboBox()
        self.combo_sort.addItems(list(self.SORT_OPTIONS.keys()))
        self.combo_sort.setStyleSheet(INPUT_STYLE)

        btn_sort = QPushButton('Sort')
        btn_sort.clicked.connect(self.sort)
        btn_sort.setStyleSheet("font-family: 'Calibri'; font-size: 16px; font-weight: bold; background-color: #B79CED; color: white;")

        layout.addWidget(self.combo_sort)
        layout.addWidget(btn_sort)

        self.setLayout(layout)
        self.setWindowTitle('Sort fics')

    def sort(self):
        key = self.SORT_OPTIONS[self.combo_sort.currentText()]
        fics.sort(key=lambda fic: fic[key].lower())
        save_fics_csv()
        self.home_screen.refresh_list()
        self.close()


class SearchScreen(QWidget):
    def __init__(self, home_screen):
        super().__init__()
        self.home_screen = home_screen
        self.initUI()
        self.setMinimumSize(QSize(320, 180))

    def initUI(self):
        self.setStyleSheet("background-color: #ebe0f8;")
        form_layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.author_input = QLineEdit()
        self.tag_input = QLineEdit()
        self.fandom_input = QLineEdit()

        for field in [self.name_input, self.author_input, self.tag_input, self.fandom_input]:
            field.setStyleSheet(INPUT_STYLE)

        btn_search = QPushButton('Search')
        btn_search.clicked.connect(self.search)
        btn_search.setStyleSheet(BTN_STYLE)

        form_layout.addRow(QLabel('Name:'), self.name_input)
        form_layout.addRow(QLabel('Author:'), self.author_input)
        form_layout.addRow(QLabel('Tag:'), self.tag_input)
        form_layout.addRow(QLabel('Fandom:'), self.fandom_input)
        form_layout.addRow(btn_search)

        # Style for the labels (skips the last row, which holds the button)
        for i in range(form_layout.rowCount() - 1):
            label = form_layout.itemAt(i, QFormLayout.LabelRole).widget()
            label.setStyleSheet(LABEL_STYLE)

        self.setLayout(form_layout)
        self.setWindowTitle('Search fic')

    def search(self):
        name = self.name_input.text().lower()
        author = self.author_input.text().lower()
        tag = self.tag_input.text().lower()
        fandom = self.fandom_input.text().lower()

        # An empty field matches everything, because '' is "in" any string
        results = [fic for fic in fics
                   if name in fic['name'].lower()
                   and author in fic['author'].lower()
                   and tag in fic['tags'].lower()
                   and fandom in fic['fandom'].lower()]

        if results:
            self.home_screen.refresh_list(results)
            self.close()
        else:
            QMessageBox.information(self, 'No results', 'No fic was found matching the given criteria.')


if __name__ == '__main__':
    load_fics_csv()
    app = QApplication(sys.argv)
    home_screen = HomeScreen()
    home_screen.show()
    sys.exit(app.exec_())