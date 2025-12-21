#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MediaFlow - 照片批处理工具
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()