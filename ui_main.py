# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(473, 634)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.convert_btn = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.convert_btn.setFont(font)
        self.convert_btn.setObjectName("convert_btn")
        self.gridLayout_4.addWidget(self.convert_btn, 4, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 3)
        self.label = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 3)
        self.coords_lbl = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.coords_lbl.setFont(font)
        self.coords_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.coords_lbl.setObjectName("coords_lbl")
        self.gridLayout_2.addWidget(self.coords_lbl, 2, 0, 1, 2)
        self.data_lbl = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.data_lbl.setFont(font)
        self.data_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.data_lbl.setObjectName("data_lbl")
        self.gridLayout_2.addWidget(self.data_lbl, 1, 0, 1, 2)
        self.comment_txt = QtWidgets.QTextEdit(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comment_txt.sizePolicy().hasHeightForWidth())
        self.comment_txt.setSizePolicy(sizePolicy)
        self.comment_txt.setMaximumSize(QtCore.QSize(16777215, 100))
        self.comment_txt.setObjectName("comment_txt")
        self.gridLayout_2.addWidget(self.comment_txt, 4, 0, 1, 3)
        self.coords_btn = QtWidgets.QPushButton(self.frame)
        self.coords_btn.setObjectName("coords_btn")
        self.gridLayout_2.addWidget(self.coords_btn, 2, 2, 1, 1)
        self.data_btn = QtWidgets.QPushButton(self.frame)
        self.data_btn.setDefault(False)
        self.data_btn.setObjectName("data_btn")
        self.gridLayout_2.addWidget(self.data_btn, 1, 2, 1, 1)
        self.gridLayout_4.addWidget(self.frame, 0, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 2)
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)
        self.compression_slider = QtWidgets.QSlider(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.compression_slider.sizePolicy().hasHeightForWidth())
        self.compression_slider.setSizePolicy(sizePolicy)
        self.compression_slider.setMinimum(1)
        self.compression_slider.setMaximum(9)
        self.compression_slider.setProperty("value", 4)
        self.compression_slider.setOrientation(QtCore.Qt.Horizontal)
        self.compression_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.compression_slider.setTickInterval(1)
        self.compression_slider.setObjectName("compression_slider")
        self.gridLayout.addWidget(self.compression_slider, 3, 0, 1, 2)
        self.label_7 = QtWidgets.QLabel(self.frame_2)
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 4, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 2)
        self.gridLayout_4.addWidget(self.frame_2, 1, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout_4.addWidget(self.progressBar, 3, 0, 1, 1)
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_8 = QtWidgets.QLabel(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_8.setFont(font)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 0, 0, 1, 3)
        self.out_lbl = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.out_lbl.setFont(font)
        self.out_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.out_lbl.setObjectName("out_lbl")
        self.gridLayout_3.addWidget(self.out_lbl, 1, 0, 1, 2)
        self.out_btn = QtWidgets.QPushButton(self.frame_3)
        self.out_btn.setObjectName("out_btn")
        self.gridLayout_3.addWidget(self.out_btn, 1, 2, 1, 1)
        self.gridLayout_4.addWidget(self.frame_3, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.data_btn, self.coords_btn)
        MainWindow.setTabOrder(self.coords_btn, self.comment_txt)
        MainWindow.setTabOrder(self.comment_txt, self.compression_slider)
        MainWindow.setTabOrder(self.compression_slider, self.out_btn)
        MainWindow.setTabOrder(self.out_btn, self.convert_btn)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Convert to hdf5"))
        self.convert_btn.setText(_translate("MainWindow", "Convert"))
        self.label_3.setText(_translate("MainWindow", "Input data"))
        self.label.setText(_translate("MainWindow", "Comment (optional)"))
        self.coords_lbl.setToolTip(_translate("MainWindow", "File with coordinates for each analyzed point"))
        self.coords_lbl.setText(_translate("MainWindow", "Coordinates file"))
        self.data_lbl.setToolTip(_translate("MainWindow", "Data file containing mass spectra"))
        self.data_lbl.setText(_translate("MainWindow", "Data file"))
        self.coords_btn.setText(_translate("MainWindow", "Browse"))
        self.data_btn.setText(_translate("MainWindow", "Browse"))
        self.label_4.setText(_translate("MainWindow", "Compression"))
        self.label_6.setToolTip(_translate("MainWindow", "Larger files but faster"))
        self.label_6.setText(_translate("MainWindow", "Low"))
        self.label_7.setToolTip(_translate("MainWindow", "Smaller files but slower"))
        self.label_7.setText(_translate("MainWindow", "High"))
        self.label_5.setText(_translate("MainWindow", "Level"))
        self.label_8.setText(_translate("MainWindow", "Output"))
        self.out_lbl.setToolTip(_translate("MainWindow", "The name of the output file"))
        self.out_lbl.setText(_translate("MainWindow", "Output file"))
        self.out_btn.setText(_translate("MainWindow", "Browse"))