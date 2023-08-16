import json
import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QMainWindow, QStyledItemDelegate

from setup.edit_timetable_setup import Ui_dialog_edit_timetable
from setup.timetable_setup import Ui_mwindow_timetable

DAYS_IN_WEEK = 7  # A 7-day week
PERIODS_PER_DAY = 6  # 6 periods per day

class CellDelegate(QStyledItemDelegate):
    """Custom delegate to style cells in the table widget."""

    def paint(self, painter, option, index):
        item = index.model().data(index, QtCore.Qt.DisplayRole)
        if item:
            painter.save()
            painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
            painter.drawRect(option.rect)
            option = QtWidgets.QStyleOptionViewItem(option)
            option.displayAlignment = QtCore.Qt.AlignCenter
            self.initStyleOption(option, index)
            super().paint(painter, option, index)
            painter.restore()

def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    mwindow_timetable = TimetableWindow()
    mwindow_timetable.show()
    sys.exit(app.exec_())

def read_lessons() -> list:
    """Reads JSON files for list of lessons to display in timetable."""
    with open("resources/timetable.json", "r") as outfile:
        try:
            timetable = json.load(outfile)
        except ValueError:
            print("Empty JSON file.")
            timetable = []

        # Adds empty dictionary values for empty timetable slots.
        missing_lessons = DAYS_IN_WEEK * PERIODS_PER_DAY - len(timetable)
        for _ in range(missing_lessons):
            lesson = {"subject": " ", "teacher": " ", "room": " "}
            timetable.append(lesson)

    return timetable

class EditTimetableDialog(QDialog, Ui_dialog_edit_timetable):
    """Sets up the Edit Timetable dialog."""

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

class TimetableWindow(QMainWindow, Ui_mwindow_timetable):
    """Sets up the Timetable main window."""

    def __init__(self) -> None:
        super().__init__()
        self.Dialog = EditTimetableDialog()
        self.timetable = read_lessons()
        self.setupUi(self)
        self.setStyleSheet(
            """QTableWidget {background-color: transparent;}
            QHeaderView::section {background-color: transparent;}
            QHeaderView {background-color: transparent;}
            QTableCornerButton::section{background-color: transparent;}"""
        )
        self.btn_edit_timetable.clicked.connect(self.open_dialog_edit_timetable)
        self.btn_clear_timetable.clicked.connect(self.clear_timetable_slot)
        self.update_timetable()

    def open_dialog_edit_timetable(self) -> None:
        """Opens the dialog window for editing the timetable."""
        self.Dialog.button_box_edit_timetable.accepted.disconnect()
        self.Dialog.button_box_edit_timetable.accepted.connect(self.save_lesson)

        # Populates the combo box with subject options.
        with open("resources/subject_list.txt", "r") as data_file:
            self.Dialog.comb_box_subject.clear()
            subject_list = data_file.readlines()
            for line in subject_list:
                self.Dialog.comb_box_subject.addItem(line.strip("\n"))
        self.Dialog.open()

    def update_timetable(self) -> None:
        """Populates the timetable with all lessons."""
        # Resizes columns and rows to fit the contents.
        self.table_widget_timetable.setRowCount(PERIODS_PER_DAY)
        self.table_widget_timetable.setColumnCount(DAYS_IN_WEEK)
        self.table_widget_timetable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.table_widget_timetable.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        delegate = CellDelegate(self.table_widget_timetable)
        self.table_widget_timetable.setItemDelegate(delegate)

        # Adds lesson details to each cell in the timetable.
        for row_index in range(PERIODS_PER_DAY):
            for column_index in range(DAYS_IN_WEEK):
                lesson = self.timetable[column_index * PERIODS_PER_DAY + row_index]
                lesson_details = (
                    (lesson["subject"])
                    + "\n"
                    + (lesson["teacher"])
                    + "\n"
                    + (lesson["room"])
                )
                cell_item = QtWidgets.QTableWidgetItem(lesson_details)
                self.table_widget_timetable.setItem(row_index, column_index, cell_item)

    def save_timetable_list(self) -> None:
        """Updates the JSON file with the current timetable list."""
        with open("resources/timetable.json", "w") as outfile:
            json.dump(self.timetable, outfile, ensure_ascii=False, indent=4)
        self.update_timetable()

    def save_lesson(self) -> None:
        """Saves the lesson to the selected timetable slot."""
        selected_row = self.table_widget_timetable.currentRow()
        selected_column = self.table_widget_timetable.currentColumn()
        lesson_subject = self.Dialog.comb_box_subject.currentText()
        lesson_teacher = self.Dialog.line_edit_teacher.text()
        lesson_room = self.Dialog.line_edit_room.text()

        # Saves lesson to selected timetable slot if length validations passed.
        if len(lesson_teacher) > 30:
            self.Dialog.lbl_instruction.setText(
                "Your teacher input exceeds 30 characters. Please try again."
            )
        elif len(lesson_room) > 20:
            self.Dialog.lbl_instruction.setText(
                "Your room input exceeds 30 characters. Please try again."
            )
        else:
            lesson = {
                "subject": lesson_subject,
                "teacher": lesson_teacher,
                "room": lesson_room,
            }
            index = selected_column * PERIODS_PER_DAY + selected_row
            self.timetable[index] = lesson
            self.save_timetable_list()
            self.Dialog.close()

    def clear_timetable_slot(self) -> None:
        """Clears the lesson from the selected timetable slot."""
        selected_row = self.table_widget_timetable.currentRow()
        selected_column = self.table_widget_timetable.currentColumn()
        index = selected_column * PERIODS_PER_DAY + selected_row
        lesson = {"subject": " ", "teacher": " ", "room": " "}
        self.timetable[index] = lesson
        self.save_timetable_list()

# Opens the main window when the program is executed.
if __name__ == "__main__":
    main()

