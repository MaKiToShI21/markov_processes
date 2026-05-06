import sys
import os
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6 import uic


STATES = ["Ц (Центральный)", "З (Заельцовский)", "О (Октябрьский)"]
SHORT_LABELS = ["Ц", "З", "О"]
DEFAULT_MATRIX = [
    [0.5, 0.3, 0.2],
    [0.2, 0.6, 0.2],
    [0.6, 0.2, 0.2],
]
DEFAULT_VECTOR = [1.0, 0.0, 0.0]


class MarkovChainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), "mainwindow.ui")
        uic.loadUi(ui_path, self)

        self._setup_tables()
        self._fill_defaults()
        self._connect_signals()

    def _setup_tables(self):
        self.matrixTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.matrixTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vectorTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vectorTable.verticalHeader().setVisible(False)

    def _fill_defaults(self):
        for j in range(3):
            item = QTableWidgetItem(str(DEFAULT_VECTOR[j]))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.vectorTable.setItem(0, j, item)

        for i in range(3):
            for j in range(3):
                item = QTableWidgetItem(str(DEFAULT_MATRIX[i][j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.matrixTable.setItem(i, j, item)

    def _connect_signals(self):
        self.calcButton.clicked.connect(self.calculate)
        self.calcAllButton.clicked.connect(self.calculate_all)
        self.resetButton.clicked.connect(self.reset)

    def get_vector(self):
        vector = np.zeros(3)
        for j in range(3):
            text = self.vectorTable.item(0, j).text().replace(",", ".")
            vector[j] = float(text)
        return vector

    def get_matrix(self):
        matrix = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                text = self.matrixTable.item(i, j).text().replace(",", ".")
                matrix[i][j] = float(text)
        return matrix

    def validate_vector(self, vector):
        for j in range(3):
            if vector[j] < 0 or vector[j] > 1:
                return False, f"Вероятность вектора [{SHORT_LABELS[j]}] = {vector[j]:.4f} вне диапазона [0, 1]"
        vec_sum = np.sum(vector)
        if not np.isclose(vec_sum, 1.0, atol=1e-6):
            return False, f"Сумма вектора начальных вероятностей должна быть равна 1, сейчас: {vec_sum:.4f}"
        return True, ""

    def validate_matrix(self, matrix):
        for i in range(3):
            row_sum = np.sum(matrix[i])
            if not np.isclose(row_sum, 1.0, atol=1e-6):
                return False, f"Сумма вероятностей в строке {i+1} [{SHORT_LABELS[i]}] должна быть равна 1, сейчас: {row_sum:.4f}"
            for j in range(3):
                if matrix[i][j] < 0 or matrix[i][j] > 1:
                    return False, f"Вероятность P[{i+1}][{j+1}] = {matrix[i][j]:.4f} вне диапазона [0, 1]"
        return True, ""

    def _determine_initial_state(self, vector):
        r = np.random.random()
        cumulative = 0.0
        for idx in range(3):
            cumulative += vector[idx]
            if r < cumulative:
                return idx
        return 2

    def calculate(self):
        try:
            vector = self.get_vector()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректные значения в векторе. Введите числа.")
            return

        try:
            matrix = self.get_matrix()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректные значения в матрице. Введите числа.")
            return

        valid, msg = self.validate_vector(vector)
        if not valid:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        valid, msg = self.validate_matrix(matrix)
        if not valid:
            QMessageBox.warning(self, "Ошибка", msg)
            return

        k = self.stepsSpin.value()
        initial_idx = self._determine_initial_state(vector)

        result = self._compute(matrix, vector, k)
        self._display_result(matrix, vector, initial_idx, k, result)

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

        k = self.stepsSpin.value()
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
            output_lines.append(f"Начальное состояние: {STATES[idx]}")
            output_lines.append(f"  P(Ц) = {result[0]:.6f}")
            output_lines.append(f"  P(З) = {result[1]:.6f}")
            output_lines.append(f"  P(О) = {result[2]:.6f}")
            output_lines.append(f"  Вероятность возврата в {STATES[idx]}: {result[idx]:.6f}")
            output_lines.append("")

        self.resultsText.setText("\n".join(output_lines))

    def _compute(self, matrix, initial_vector, k):
        matrix_k = np.linalg.matrix_power(matrix, k)
        return initial_vector @ matrix_k

    def _format_matrix(self, matrix):
        lines = []
        header = "       Ц        З        О"
        lines.append(header)
        for i in range(3):
            row_str = f"  {SHORT_LABELS[i]}  " + "  ".join(f"{matrix[i][j]:.4f}" for j in range(3))
            lines.append(row_str)
        return "\n".join(lines)

    def _display_result(self, matrix, vector, initial_idx, k, result):
        output_lines = []
        r_info = f"Начальный район: {STATES[initial_idx]}"
        output_lines.append(r_info)
        output_lines.append(f"Вектор начальных вероятностей: [{vector[0]:.2f}, {vector[1]:.2f}, {vector[2]:.2f}]")
        output_lines.append(f"Количество шагов: k = {k}")
        output_lines.append("")

        matrix_k = np.linalg.matrix_power(matrix, k)
        output_lines.append(f"Матрица переходов P^{k}:")
        output_lines.append(self._format_matrix(matrix_k))
        output_lines.append("")

        output_lines.append("Пошаговый расчёт:")
        current = vector.copy()
        for step in range(1, k + 1):
            current = current @ matrix
            output_lines.append(f"  Шаг {step}: P(Ц)={current[0]:.6f}  P(З)={current[1]:.6f}  P(О)={current[2]:.6f}")

        output_lines.append(f"\n{'─'*60}")
        output_lines.append(f"Итоговые вероятности после {k} шагов:")
        output_lines.append(f"  P(Ц) = {result[0]:.6f}")
        output_lines.append(f"  P(З) = {result[1]:.6f}")
        output_lines.append(f"  P(О) = {result[2]:.6f}")

        self.resultsText.setText("\n".join(output_lines))

    def reset(self):
        self._fill_defaults()
        self.resultsText.clear()


def main():
    app = QApplication(sys.argv)
    window = MarkovChainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
