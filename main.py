import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget,
                             QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLineEdit, QShortcut,
                             QTextEdit, QDialog, QStackedWidget, QStyle)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QSize
import operators as op


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()

        self.calc_page = CalculatorPage()
        self.history_page = HistoryPage()

        self.stack.addWidget(self.calc_page)
        self.stack.addWidget(self.history_page)

        self.setCentralWidget(self.stack)

        self.calc_page.history_btn.clicked.connect(self.show_history)
        self.history_page.back_btn.clicked.connect(self.show_calculator)

        self.setGeometry(0, 0, 450, 500)

    def show_history(self):
        histories = op.load_histories()
        self.history_page.load_text(histories)
        self.stack.setCurrentIndex(1)

    def show_calculator(self):
        self.stack.setCurrentIndex(0)


# Calculator_Page
class CalculatorPage(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)


        self.history_btn = QPushButton("Show History")
        self.history_btn.setFixedHeight(36)
        main_layout.addWidget(self.history_btn, alignment=Qt.AlignRight)
        self.history_btn.setMaximumWidth(140)


        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setMinimumHeight(100)
        display_font = QFont()
        display_font.setPointSize(20)
        self.display.setFont(display_font)
        main_layout.addWidget(self.display)


        grid = QGridLayout()
        grid.setSpacing(8)
        main_layout.addLayout(grid)

        buttons = [
            ["√", "π", "^", "!"],
            ["AC", "()", "%","÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "⌫","=" ]
        ]

        self.buttons = []

        btn_font = QFont()
        btn_font.setPointSize(20)

        for row, row_value in enumerate(buttons):
            for col, text in enumerate(row_value):

                btn = QPushButton(text)
                btn.setMinimumHeight(100)
                btn.setFont(btn_font)
                self.buttons.append(btn)

                if text == "⌫":
                    icon = self.style().standardIcon(QStyle.SP_LineEditClearButton)
                    btn.setIcon(icon)
                    btn.setText("")
                    btn.setIconSize(QSize(24, 24))

                btn.setStyleSheet("""
                    QPushButton {
                        border-radius: 12px;
                        border: 1px solid #aaa;
                    }
                    QPushButton:hover {
                        background-color: #e6e6e6;
                    }              
                """)

                grid.addWidget(btn, row, col)

                btn.clicked.connect(lambda _, t=text: self.handle_button(t))


    def add_text(self, t):
        self.display.setText(self.display.text() + t)

    def handle_button(self, t):

        if t == "AC":
            self.display.clear()
            self.enable_all_button()
            return

        if t == "⌫":
            self.display.setText(self.display.text()[:-1])
            return

        if t == "√":
            self.add_text("√(")
            return

        if t == "=":

            expr = self.display.text()
            raw_expr = expr

            if not expr:
                return

            elif expr[-1] in "+-×÷":
                expr = expr[:-1]

            expr = (expr.replace("×", "*")
                    .replace("÷", "/")
                    .replace("^", "**")
                    .replace("√", "sqrt")
                    .replace("π", "pi"))
            expr = re.sub(r"(\d|\))\(", r"\1*(", expr)
            expr = re.sub(r'(\d+)!', r'fact(\1)', expr)
            expr = re.sub(r'sqrt(\d+(\.\d+)?)', r'sqrt(\1)', expr)

            if "sqrt(" in expr and expr.count("(") != expr.count(")"):
                self.display.setText("Incomplete sqrt")
                return

            try:
                expression = expr
                answer = op.eval_expr(expr)
                print("EVAL EXPR:", expr)
                if isinstance(answer, float):
                    answer = f"{answer:.6f}".rstrip("0").rstrip(".")

                self.display.setText(str(answer))

                history = op.load_histories()
                history.append({
                    "expression": raw_expr, "answer": answer
                })
                op.add_history(history)
                self.disable_after_equal()

            except ZeroDivisionError:
                self.display.setText("Cannot divide by zero")
                return

            except ValueError as e:
                self.display.setText(str(e))
                return

            except Exception:
                self.display.setText("Invalid expression")
                return

            self.disable_after_equal()
            return

        if t == "()":
            self.smart_parenthesis()
            return

        if t in self.OPS:
            self.can_add_operator(t)
            return


        self.add_text(t)

    def smart_parenthesis(self):
        t = self.display.text()

        open_count = t.count("(")
        close_count = t.count(")")

        if not t:
            self.add_text("(")
            return

        last = t[-1]

        if open_count > close_count and last.isdigit():
            self.add_text(")")

        else:
            self.add_text("(")

    OPS = "+-×÷%^!"

    def can_add_operator(self, op):
        t = self.display.text()

        if not t:
            if op == "-":
                self.add_text("-")
                return

        last = t[-1]

        if last in self.OPS:

            if last in "×÷" and op == "-":
                self.add_text("-")
                return

            self.display.setText(t[:-1] + op)
            return

        self.add_text(op)

    def disable_after_equal(self):
        for b in self.buttons:
            if b.text() != "AC":
                b.setEnabled(False)

    def enable_all_button(self):
        for b in self.buttons:
            b.setEnabled(True)


# History_Page
class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        self.back_btn = QPushButton("Back")
        self.back_btn.setFixedHeight(36)
        layout.addWidget(self.back_btn, alignment=Qt.AlignHCenter)
        self.back_btn.setMaximumWidth(130)

        layout.addWidget(self.text)
        layout.addWidget(self.back_btn)

        self.text.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                line-height: 150%;
            }
        """)

    history_font = QFont()
    history_font.setPointSize(19)

    def load_text(self, histories):
        lines = ""
        self.text.setFont(self.history_font)

        for h in histories:
            lines += f"\n {h['expression']}\n = {h['answer']}\n ____________\n"


        self.text.setText(lines)




def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()