from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QTextEdit, QComboBox,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MarkovChainUI(QMainWindow):
    STATES = ["Ц (Центральный)", "З (Заельцовский)", "О (Октябрьский)"]
    SHORT_LABELS = ["Ц", "З", "О"]
    DEFAULT_MATRIX = [
        [0.5, 0.3, 0.2],
        [0.2, 0.6, 0.2],
        [0.6, 0.2, 0.2],
    ]

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Марковские процессы — Маршрут курьера")
        self.setMinimumSize(750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)

        self._setup_matrix_group(main_layout)
        self._setup_params_group(main_layout)
        self._setup_buttons(main_layout)
        self._setup_results(main_layout)

        self._fill_default_matrix()

    def _setup_matrix_group(self, parent_layout):
        matrix_group = QGroupBox("Матрица переходных вероятностей")
        matrix_layout = QVBoxLayout(matrix_group)

        self.matrix_table = QTableWidget(3, 3)
        self.matrix_table.setHorizontalHeaderLabels(self.SHORT_LABELS)
        self.matrix_table.setVerticalHeaderLabels(self.SHORT_LABELS)
        self.matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matrix_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matrix_table.setFixedHeight(130)

        matrix_layout.addWidget(self.matrix_table)
        parent_layout.addWidget(matrix_group)

    def _setup_params_group(self, parent_layout):
        params_group = QGroupBox("Параметры")
        params_layout = QGridLayout(params_group)

        params_layout.addWidget(QLabel("Начальное состояние:"), 0, 0)
        self.initial_state_combo = QComboBox()
        self.initial_state_combo.addItems(self.STATES)
        params_layout.addWidget(self.initial_state_combo, 0, 1)

        params_layout.addWidget(QLabel("Количество шагов (k):"), 1, 0)
        self.steps_spin = QSpinBox()
        self.steps_spin.setMinimum(1)
        self.steps_spin.setMaximum(100)
        self.steps_spin.setValue(3)
        params_layout.addWidget(self.steps_spin, 1, 1)

        parent_layout.addWidget(params_group)

    def _setup_buttons(self, parent_layout):
        buttons_layout = QHBoxLayout()

        self.calc_button = QPushButton("Рассчитать")
        self.calc_button.setFixedHeight(36)
        buttons_layout.addWidget(self.calc_button)

        self.calc_all_button = QPushButton("Рассчитать для всех начальных состояний")
        self.calc_all_button.setFixedHeight(36)
        buttons_layout.addWidget(self.calc_all_button)

        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setFixedHeight(36)
        buttons_layout.addWidget(self.reset_button)

        parent_layout.addLayout(buttons_layout)

    def _setup_results(self, parent_layout):
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        results_layout.addWidget(self.results_text)

        parent_layout.addWidget(results_group)

    def _fill_default_matrix(self):
        for i in range(3):
            for j in range(3):
                item = QTableWidgetItem(str(self.DEFAULT_MATRIX[i][j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.matrix_table.setItem(i, j, item)
