import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt

from ui import MarkovChainUI


class MarkovChainApp(MarkovChainUI):
    def __init__(self):
        super().__init__()
        self._connect_signals()

    def _connect_signals(self):
        self.calc_button.clicked.connect(self.calculate)
        self.calc_all_button.clicked.connect(self.calculate_all)
        self.reset_button.clicked.connect(self.reset_matrix)

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
                return False, f"Сумма вероятностей в строке {i+1} ({self.STATES[i]}) = {row_sum:.4f} ≠ 1"
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
            output_lines.append(f"Начальное состояние: {self.STATES[idx]}")
            output_lines.append(f"  P(Ц) = {result[0]:.6f}")
            output_lines.append(f"  P(З) = {result[1]:.6f}")
            output_lines.append(f"  P(О) = {result[2]:.6f}")
            output_lines.append(f"  Вероятность возврата в {self.STATES[idx]}: {result[idx]:.6f}")
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
        output_lines.append(f"Начальное состояние: {self.STATES[initial_idx]}")
        output_lines.append(f"Количество шагов: k = {k}")

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
        output_lines.append(f"\n Вероятность возврата в {self.STATES[initial_idx]}: {result[initial_idx]:.6f}")

        self.results_text.setText("\n".join(output_lines))

    def reset_matrix(self):
        self._fill_default_matrix()
        self.results_text.clear()


def main():
    app = QApplication(sys.argv)
    window = MarkovChainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
