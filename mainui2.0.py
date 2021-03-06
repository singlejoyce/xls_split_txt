# -*- coding:utf-8 -*-
"""
Basic Layout
"""
import sys
from PyQt5 import QtGui, Qt
from PyQt5.QtWidgets import *
from mythread import *

__author__ = "joyce"


class MyQTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(None, parent)
        self.text_list = []
        self.setAcceptDrops(True)
        # self.setDragEnabled(True)  # 开启可拖放事件

    def dragEnterEvent(self, QDragEnterEvent):
        e = QDragEnterEvent  # type:QDragEnterEvent
        # print('type:', e.type())  # 事件的类型
        # print('pos:', e.pos())  # 拖放位置
        # print(e.mimeData().urls())  # 文件所有的路径
        # print(e.mimeData().text())  # 文件路径
        # print(e.mimeData().formats())  # 支持的所有格式
        # print(e.mimeData().data('text/plain'))  # 根据mime类型取路径 值为字节数组
        # print(e.mimeData().hasText())  # 是否支持文本文件格式
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        text = e.mimeData().text().replace('file:///', '')
        self.setText(text)
        if text.find("\n") == -1:  # 没找到"\n",即单个文件的处理
            self.text_list = text.split("\n")
        else:
            self.text_list = text.split("\n")[:-1]


class MainUi(QMainWindow):
    def __init__(self, parent=None):
        super(MainUi, self).__init__(parent)
        self.xls_dir_list = ""
        self.resize(1066, 784)
        self.setWindowTitle('xls拆分sheet工具2.0')
        self.xls_path_l = QLineEdit("D:\\project\\LoveDance_N1\\data\\xlsx")
        self.xls_path_r = QLineEdit("D:\\project\\LoveDance_P1\\data\\xlsx")
        self.xls_dir_l = MyQTextEdit()
        self.xls_dir_r = MyQTextEdit()
        self.startButton = QPushButton("开始")
        self.selectButton = QPushButton("选择xls文件")
        self.selectButton.clicked.connect(self.btn_chooseMutiFile)
        self.startButton.clicked.connect(self.startWork)

        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet('QStatusBar::item {border: none;}')
        self.setStatusBar(self.statusBar)
        self.progressBar = QProgressBar()
        self.progressBarlabel1 = QLabel("状态")
        self.progressBarlabel2 = QLabel("正在计算：")
        self.statusBar.addPermanentWidget(self.progressBarlabel1, stretch=2)
        self.statusBar.addPermanentWidget(self.progressBarlabel2, stretch=0)
        self.statusBar.addPermanentWidget(self.progressBar, stretch=4)
        self.progressBar.setRange(0, 100)  # 设置进度条的范围
        self.progressBar.setValue(0)

        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        self.setFont(font)

        self.retranslateUi()

    def retranslateUi(self):
        pathGroupBox = QGroupBox("xls文件起始路径：")
        pathGroupBox1 = QGroupBox("Left：")
        pathGroupBox2 = QGroupBox("Right：")
        dirGroupBox = QGroupBox("xls文件地址：")
        dirGroupBox1 = QGroupBox("Left：")
        dirGroupBox2 = QGroupBox("Right：")
        btnGroupBox = QGroupBox("")

        layout = QVBoxLayout()
        layout.addWidget(self.xls_path_l)
        pathGroupBox1.setLayout(layout)

        layout = QVBoxLayout()
        layout.addWidget(self.xls_path_r)
        pathGroupBox2.setLayout(layout)

        layout = QVBoxLayout()
        layout.addWidget(pathGroupBox1)
        layout.addWidget(pathGroupBox2)
        pathGroupBox.setLayout(layout)

        layout = QVBoxLayout()
        layout.addWidget(self.xls_dir_l)
        dirGroupBox1.setLayout(layout)

        layout = QVBoxLayout()
        layout.addWidget(self.xls_dir_r)
        dirGroupBox2.setLayout(layout)

        layout = QHBoxLayout()
        layout.addWidget(dirGroupBox1)
        layout.addWidget(dirGroupBox2)
        dirGroupBox.setLayout(layout)

        layout = QHBoxLayout()
        layout.addWidget(self.selectButton)
        layout.addWidget(self.startButton)
        btnGroupBox.setLayout(layout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(pathGroupBox)
        mainLayout.addWidget(dirGroupBox)
        mainLayout.addWidget(btnGroupBox)

        main_frame = QWidget()
        main_frame.setLayout(mainLayout)
        self.setCentralWidget(main_frame)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', '确认退出吗？',
                                     QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Ok:
            event.accept()
        elif reply == QMessageBox.Cancel:
            event.ignore()

    def btn_chooseMutiFile(self):
        self.xls_dir_l.clear()
        self.xls_dir_r.clear()

        self.xls_dir_list_l, filetype = QFileDialog.getOpenFileNames(self, "文件选择Left", self.xls_path_l.text(), 'Excel files(*.xlsx , *.xls)')
        self.xls_dir_l.text_list = self.xls_dir_list_l
        for file in self.xls_dir_list_l:
            self.xls_dir_l.append(file)

        self.xls_dir_list_r, filetype = QFileDialog.getOpenFileNames(self, "文件选择Right", self.xls_path_r.text(), 'Excel files(*.xlsx , *.xls)')

        self.xls_dir_r.text_list = self.xls_dir_list_r
        for file in self.xls_dir_list_r:
            self.xls_dir_r.append(file)

    def updateProgressBar(self, text):
        # print("%s: 进度：%s" % (time.strftime('%H:%M:%S', time.localtime(time.time())), int(text)))
        if int(text) < 90:
            self.progressBar.setValue(int(text))
        else:
            self.progressBar.setValue(90)

    def finishWork(self):
        self.progressthread.finish_state = True
        self.progressBar.setValue(100)
        QMessageBox.information(self, "提示", self.tr("xls文件拆分完成!"), QMessageBox.Ok)

    def startWork(self):
        self.progressBar.setValue(0)
        self.xls_dir_list_l = self.xls_dir_l.text_list
        self.xls_dir_list_r = self.xls_dir_r.text_list

        # 如果xls未选择进行警告提示
        if len(self.xls_dir_list_l) == 0 and len(self.xls_dir_list_r) == 0:
            reply = QMessageBox.critical(self, "提示", self.tr("未选择需拆分的xls文件!"), QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                return

        # 更新进度条操作的线程
        self.progressthread = MyThread()
        self.progressthread.update_progressBar_signal.connect(self.updateProgressBar)
        self.progressthread.start()

        # 处理excel操作的线程，防止ui界面卡住
        self.workthread = WorkThread2(self.xls_dir_list_l, self.xls_dir_list_r)
        self.workthread.finish_state_signal.connect(self.finishWork)
        self.workthread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUi()
    ex.show()
    sys.exit(app.exec_())

