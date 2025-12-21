#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的PyQt5测试
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('PyQt5测试窗口')
    window.setGeometry(100, 100, 300, 200)
    
    layout = QVBoxLayout()
    label = QLabel('如果你能看到这个窗口，说明PyQt5正常工作！')
    label.setAlignment(Qt.AlignCenter)
    layout.addWidget(label)
    
    window.setLayout(layout)
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()