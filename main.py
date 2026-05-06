import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QTextEdit, QComboBox,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MarkovChainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.states = ["Ц (Центральный)", "З (Заельцовский)", "О (Октябрьский)"]
        self.default_matrix = [
            [0.5, 0.3, 0.2],
            [0.2, 0.6, 0.2],
            [0.6, 0.2, 0.2],
        ]
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Марковские процессы — Маршрут курьера")
        self.setMinimumSize(750, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)

        # --- Transition matrix ---
        matrix_group = QGroupBox("Матрица переходных вероятностей")
        matrix_layout = QVBoxLayout(matrix_group)

        self.matrix_table = QTableWidget(3, 3)
        short_labels = ["Ц", "З", "О"]
        self.matrix_table.setHorizontalHeaderLabels(short_labels)
        self.matrix_table.setVerticalHeaderLabels(short_labels)
        self.matrix_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matrix_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matrix_table.setFixedHeight(130)

        for i in range(3):
            for j in range(3):
                item = QTableWidgetItem(str(self.default_matrix[i][j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.matrix_table.setItem(i, j, item)

        matrix_layout.addWidget(self.matrix_table)
        main_layout.addWidget(matrix_group)

        # --- Initial state and iterations ---
        params_group = QGroupBox("Параметры")
        params_layout = QGridLayout(params_group)

        params_layout.addWidget(QLabel("Начальное состояние:"), 0, 0)
        self.initial_state_combo = QComboBox()
        self.initial_state_combo.addItems(self.states)
        params_layout.addWidget(self.initial_state_combo, 0, 1)

        params_layout.addWidget(QLabel("Количество шагов (k):"), 1, 0)
        self.steps_spin = QSpinBox()
        self.steps_spin.setMinimum(1)
        self.steps_spin.setMaximum(100)
        self.steps_spin.setValue(3)
        params_layout.addWidget(self.steps_spin, 1, 1)

        main_layout.addWidget(params_group)

        # --- Buttons ---
        buttons_layout = QHBoxLayout()

        self.calc_button = QPushButton("Рассчитать")
        self.calc_button.setFixedHeight(36)
        self.calc_button.clicked.connect(self.calculate)
        buttons_layout.addWidget(self.calc_button)

        self.calc_all_button = QPushButton("Рассчитать для всех начальных состояний")
        self.calc_all_button.setFixedHeight(36)
        self.calc_all_button.clicked.connect(self.calculate_all)
        buttons_layout.addWidget(self.calc_all_button)

        self.reset_button = QPushButton("Сбросить")
        self.reset_button.setFixedHeight(36)
        self.reset_button.clicked.connect(self.reset_matrix)
        buttons_layout.addWidget(self.reset_button)

        main_layout.addLayout(buttons_layout)

        # --- Results ---
        results_group = QGroupBox("Результаты")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Consolas", 10))
        results_layout.addWidget(self.results_text)

        main_layout.addWidget(results_group)

    def get_matrix(self):
        matrix = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                text = self.matrix_table.item(i, j).text().replace(",", ".")
                matrix[i][j] = float(text)
        return matrix

    def validate_matrix(self, matrix):
        for i in range(3):
            row_sum = np.sum(matrix[i])
            if not np.isclose(row_sum, 1.0, atol=1e-6):
                return False, f"Сумма вероятностей в строке {i+1} ({self.states[i]}) = {row_sum:.4f} ≠ 1"
            for j in range(3):
                if matrix[i][j] < 0 or matrix[i][j] > 1:
                    return False, f"Вероятность P[{i+1}][{j+1}] = {matrix[i][j]:.4f} вне диапазона [0, 1]"
        return True, ""

    def calculate(self):
        try:
            matrix = self.get_matrix()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректные значения в матрице. Введите числа.")
            return

        valid, msg = self.validate_matrix(matrix)
        if not valid:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        k = self.steps_spin.value()
        initial_idx = self.initial_state_combo.currentIndex()

        initial_vector = np.zeros(3)
        initial_vector[initial_idx] = 1.0

        result = self._compute(matrix, initial_vector, k)
        self._display_result(matrix, initial_vector, initial_idx, k, result)

    def calculate_all(self):
        try:
            matrix = self.get_matrix()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректные значения в матрице. Введите числа.")
            return

        valid, msg = self.validate_matrix(matrix)
        if not valid:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        k = self.steps_spin.value()
        output_lines = []
        output_lines.append(f"Результаты для всех начальных состояний (k = {k})")

        matrix_k = np.linalg.matrix_power(matrix, k)
        output_lines.append(f"Матрица переходов P^{k}:")
        output_lines.append(self._format_matrix(matrix_k))
        output_lines.append("")

        for idx in range(3):
            initial_vector = np.zeros(3)
            initial_vector[idx] = 1.0
            result = self._compute(matrix, initial_vector, k)

            output_lines.append(f"{'─'*60}")
            output_lines.append(f"Начальное состояние: {self.states[idx]}")
            output_lines.append(f"  P(Ц) = {result[0]:.6f}")
            output_lines.append(f"  P(З) = {result[1]:.6f}")
            output_lines.append(f"  P(О) = {result[2]:.6f}")
            output_lines.append(f"  Вероятность возврата в {self.states[idx]}: {result[idx]:.6f}")
            output_lines.append("")

        self.results_text.setText("\n".join(output_lines))

    def _compute(self, matrix, initial_vector, k):
        matrix_k = np.linalg.matrix_power(matrix, k)
        return initial_vector @ matrix_k

    def _format_matrix(self, matrix):
        lines = []
        header = "       Ц        З        О"
        lines.append(header)
        labels = ["Ц", "З", "О"]
        for i in range(3):
            row_str = f"  {labels[i]}  " + "  ".join(f"{matrix[i][j]:.4f}" for j in range(3))
            lines.append(row_str)
        return "\n".join(lines)

    def _display_result(self, matrix, initial_vector, initial_idx, k, result):
        output_lines = []
        output_lines.append(f"{'='*60}")
        output_lines.append(f"Начальное состояние: {self.states[initial_idx]}")
        output_lines.append(f"Количество шагов: k = {k}")
        output_lines.append(f"{'='*60}\n")

        matrix_k = np.linalg.matrix_power(matrix, k)
        output_lines.append(f"Матрица переходов P^{k}:")
        output_lines.append(self._format_matrix(matrix_k))
        output_lines.append("")

        output_lines.append("Пошаговый расчёт:")
        current = initial_vector.copy()
        for step in range(1, k + 1):
            current = current @ matrix
            output_lines.append(f"  Шаг {step}: P(Ц)={current[0]:.6f}  P(З)={current[1]:.6f}  P(О)={current[2]:.6f}")

        output_lines.append(f"\n{'─'*60}")
        output_lines.append(f"Итоговые вероятности после {k} шагов:")
        output_lines.append(f"  P(Ц) = {result[0]:.6f}")
        output_lines.append(f"  P(З) = {result[1]:.6f}")
        output_lines.append(f"  P(О) = {result[2]:.6f}")
        output_lines.append(f"\n  → Вероятность возврата в {self.states[initial_idx]}: {result[initial_idx]:.6f}")

        self.results_text.setText("\n".join(output_lines))

    def reset_matrix(self):
        for i in range(3):
            for j in range(3):
                item = QTableWidgetItem(str(self.default_matrix[i][j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.matrix_table.setItem(i, j, item)
        self.results_text.clear()


def main():
    app = QApplication(sys.argv)
    window = MarkovChainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
