# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/converter.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Converter(object):
    def setupUi(self, Converter):
        Converter.setObjectName("Converter")
        Converter.resize(1004, 898)
        self.centralwidget = QtWidgets.QWidget(Converter)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_5.addWidget(self.label_6)
        self.cmd_roi = QtWidgets.QComboBox(self.centralwidget)
        self.cmd_roi.setObjectName("cmd_roi")
        self.horizontalLayout_5.addWidget(self.cmd_roi)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.chk_omega = QtWidgets.QCheckBox(self.groupBox)
        self.chk_omega.setChecked(True)
        self.chk_omega.setObjectName("chk_omega")
        self.gridLayout.addWidget(self.chk_omega, 1, 0, 1, 1)
        self.chk_chi = QtWidgets.QCheckBox(self.groupBox)
        self.chk_chi.setChecked(True)
        self.chk_chi.setObjectName("chk_chi")
        self.gridLayout.addWidget(self.chk_chi, 1, 1, 1, 1)
        self.chk_mu = QtWidgets.QCheckBox(self.groupBox)
        self.chk_mu.setChecked(False)
        self.chk_mu.setObjectName("chk_mu")
        self.gridLayout.addWidget(self.chk_mu, 1, 2, 1, 1)
        self.chk_phi = QtWidgets.QCheckBox(self.groupBox)
        self.chk_phi.setChecked(True)
        self.chk_phi.setObjectName("chk_phi")
        self.gridLayout.addWidget(self.chk_phi, 2, 1, 1, 1)
        self.chk_omega_t = QtWidgets.QCheckBox(self.groupBox)
        self.chk_omega_t.setObjectName("chk_omega_t")
        self.gridLayout.addWidget(self.chk_omega_t, 2, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.sb_energy = QtWidgets.QSpinBox(self.centralwidget)
        self.sb_energy.setEnabled(True)
        self.sb_energy.setMinimum(2400)
        self.sb_energy.setMaximum(35000)
        self.sb_energy.setSingleStep(100)
        self.sb_energy.setObjectName("sb_energy")
        self.horizontalLayout_3.addWidget(self.sb_energy)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.widget_4 = QtWidgets.QWidget(self.centralwidget)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_7 = QtWidgets.QLabel(self.widget_4)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_6.addWidget(self.label_7)
        self.cmb_detector_rotation = QtWidgets.QComboBox(self.widget_4)
        self.cmb_detector_rotation.setObjectName("cmb_detector_rotation")
        self.cmb_detector_rotation.addItem("")
        self.cmb_detector_rotation.addItem("")
        self.horizontalLayout_6.addWidget(self.cmb_detector_rotation)
        self.verticalLayout.addWidget(self.widget_4)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.sb_cen_x = QtWidgets.QSpinBox(self.groupBox_2)
        self.sb_cen_x.setEnabled(True)
        self.sb_cen_x.setMinimum(0)
        self.sb_cen_x.setMaximum(10000)
        self.sb_cen_x.setSingleStep(1)
        self.sb_cen_x.setProperty("value", 1161)
        self.sb_cen_x.setObjectName("sb_cen_x")
        self.horizontalLayout.addWidget(self.sb_cen_x)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.sb_cen_y = QtWidgets.QSpinBox(self.groupBox_2)
        self.sb_cen_y.setEnabled(True)
        self.sb_cen_y.setMinimum(0)
        self.sb_cen_y.setMaximum(10000)
        self.sb_cen_y.setSingleStep(1)
        self.sb_cen_y.setProperty("value", 290)
        self.sb_cen_y.setObjectName("sb_cen_y")
        self.horizontalLayout.addWidget(self.sb_cen_y)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.groupBox_3)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.dsb_size_x = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.dsb_size_x.setEnabled(True)
        self.dsb_size_x.setDecimals(2)
        self.dsb_size_x.setProperty("value", 55.0)
        self.dsb_size_x.setObjectName("dsb_size_x")
        self.horizontalLayout_2.addWidget(self.dsb_size_x)
        self.label_5 = QtWidgets.QLabel(self.groupBox_3)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.dsb_size_y = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.dsb_size_y.setEnabled(True)
        self.dsb_size_y.setDecimals(2)
        self.dsb_size_y.setProperty("value", 55.0)
        self.dsb_size_y.setObjectName("dsb_size_y")
        self.horizontalLayout_2.addWidget(self.dsb_size_y)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_9 = QtWidgets.QLabel(self.groupBox_5)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 0, 0, 1, 1)
        self.dsb_det_d = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.dsb_det_d.setEnabled(True)
        self.dsb_det_d.setDecimals(5)
        self.dsb_det_d.setProperty("value", 0.96279)
        self.dsb_det_d.setObjectName("dsb_det_d")
        self.gridLayout_3.addWidget(self.dsb_det_d, 0, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_5)
        self.label_8.setObjectName("label_8")
        self.gridLayout_3.addWidget(self.label_8, 1, 0, 1, 1)
        self.dsb_det_r = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.dsb_det_r.setEnabled(True)
        self.dsb_det_r.setDecimals(5)
        self.dsb_det_r.setMinimum(-360.0)
        self.dsb_det_r.setMaximum(360.0)
        self.dsb_det_r.setProperty("value", 0.0)
        self.dsb_det_r.setObjectName("dsb_det_r")
        self.gridLayout_3.addWidget(self.dsb_det_r, 1, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_5)
        self.label_10.setObjectName("label_10")
        self.gridLayout_3.addWidget(self.label_10, 2, 0, 1, 1)
        self.dsb_det_rt = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.dsb_det_rt.setEnabled(True)
        self.dsb_det_rt.setDecimals(5)
        self.dsb_det_rt.setMinimum(-360.0)
        self.dsb_det_rt.setMaximum(360.0)
        self.dsb_det_rt.setProperty("value", 0.0)
        self.dsb_det_rt.setObjectName("dsb_det_rt")
        self.gridLayout_3.addWidget(self.dsb_det_rt, 2, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox_5)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 3, 0, 1, 1)
        self.dsb_det_t = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.dsb_det_t.setEnabled(True)
        self.dsb_det_t.setDecimals(5)
        self.dsb_det_t.setMinimum(-360.0)
        self.dsb_det_t.setMaximum(360.0)
        self.dsb_det_t.setProperty("value", 0.0)
        self.dsb_det_t.setObjectName("dsb_det_t")
        self.gridLayout_3.addWidget(self.dsb_det_t, 3, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_5)
        self.groupBox_6 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.dsb_shift_omega = QtWidgets.QDoubleSpinBox(self.groupBox_6)
        self.dsb_shift_omega.setEnabled(True)
        self.dsb_shift_omega.setDecimals(5)
        self.dsb_shift_omega.setMinimum(-360.0)
        self.dsb_shift_omega.setMaximum(360.0)
        self.dsb_shift_omega.setObjectName("dsb_shift_omega")
        self.gridLayout_4.addWidget(self.dsb_shift_omega, 0, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_6)
        self.label_12.setObjectName("label_12")
        self.gridLayout_4.addWidget(self.label_12, 0, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_6)
        self.label_13.setObjectName("label_13")
        self.gridLayout_4.addWidget(self.label_13, 1, 0, 1, 1)
        self.dsb_shift_chi = QtWidgets.QDoubleSpinBox(self.groupBox_6)
        self.dsb_shift_chi.setEnabled(True)
        self.dsb_shift_chi.setDecimals(5)
        self.dsb_shift_chi.setMinimum(-360.0)
        self.dsb_shift_chi.setMaximum(360.0)
        self.dsb_shift_chi.setObjectName("dsb_shift_chi")
        self.gridLayout_4.addWidget(self.dsb_shift_chi, 1, 1, 1, 1)
        self.dsb_shift_gamma = QtWidgets.QDoubleSpinBox(self.groupBox_6)
        self.dsb_shift_gamma.setEnabled(True)
        self.dsb_shift_gamma.setDecimals(5)
        self.dsb_shift_gamma.setMinimum(-360.0)
        self.dsb_shift_gamma.setMaximum(360.0)
        self.dsb_shift_gamma.setProperty("value", 0.0)
        self.dsb_shift_gamma.setObjectName("dsb_shift_gamma")
        self.gridLayout_4.addWidget(self.dsb_shift_gamma, 3, 1, 1, 1)
        self.dsb_shift_phi = QtWidgets.QDoubleSpinBox(self.groupBox_6)
        self.dsb_shift_phi.setEnabled(True)
        self.dsb_shift_phi.setDecimals(5)
        self.dsb_shift_phi.setMinimum(-360.0)
        self.dsb_shift_phi.setMaximum(360.0)
        self.dsb_shift_phi.setProperty("value", 0.0)
        self.dsb_shift_phi.setObjectName("dsb_shift_phi")
        self.gridLayout_4.addWidget(self.dsb_shift_phi, 2, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox_6)
        self.label_14.setObjectName("label_14")
        self.gridLayout_4.addWidget(self.label_14, 2, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.groupBox_6)
        self.label_15.setObjectName("label_15")
        self.gridLayout_4.addWidget(self.label_15, 3, 0, 1, 1)
        self.label_16 = QtWidgets.QLabel(self.groupBox_6)
        self.label_16.setObjectName("label_16")
        self.gridLayout_4.addWidget(self.label_16, 4, 0, 1, 1)
        self.dsb_shift_delta = QtWidgets.QDoubleSpinBox(self.groupBox_6)
        self.dsb_shift_delta.setEnabled(True)
        self.dsb_shift_delta.setDecimals(5)
        self.dsb_shift_delta.setMinimum(-360.0)
        self.dsb_shift_delta.setMaximum(360.0)
        self.dsb_shift_delta.setObjectName("dsb_shift_delta")
        self.gridLayout_4.addWidget(self.dsb_shift_delta, 4, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_6)
        self.groupBox_7 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_7.setObjectName("groupBox_7")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_7)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.sb_bin_y = QtWidgets.QSpinBox(self.groupBox_7)
        self.sb_bin_y.setEnabled(True)
        self.sb_bin_y.setMaximum(1000)
        self.sb_bin_y.setProperty("value", 152)
        self.sb_bin_y.setObjectName("sb_bin_y")
        self.gridLayout_5.addWidget(self.sb_bin_y, 1, 1, 1, 1)
        self.sb_bin_z = QtWidgets.QSpinBox(self.groupBox_7)
        self.sb_bin_z.setEnabled(True)
        self.sb_bin_z.setMaximum(1000)
        self.sb_bin_z.setProperty("value", 153)
        self.sb_bin_z.setObjectName("sb_bin_z")
        self.gridLayout_5.addWidget(self.sb_bin_z, 2, 1, 1, 1)
        self.sb_bin_x = QtWidgets.QSpinBox(self.groupBox_7)
        self.sb_bin_x.setEnabled(True)
        self.sb_bin_x.setMaximum(1000)
        self.sb_bin_x.setProperty("value", 151)
        self.sb_bin_x.setObjectName("sb_bin_x")
        self.gridLayout_5.addWidget(self.sb_bin_x, 0, 1, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.groupBox_7)
        self.label_17.setObjectName("label_17")
        self.gridLayout_5.addWidget(self.label_17, 0, 0, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.groupBox_7)
        self.label_18.setObjectName("label_18")
        self.gridLayout_5.addWidget(self.label_18, 1, 0, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.groupBox_7)
        self.label_19.setObjectName("label_19")
        self.gridLayout_5.addWidget(self.label_19, 2, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_7)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.cmd_preview = QtWidgets.QPushButton(self.centralwidget)
        self.cmd_preview.setObjectName("cmd_preview")
        self.verticalLayout.addWidget(self.cmd_preview)
        self.cmd_save = QtWidgets.QPushButton(self.centralwidget)
        self.cmd_save.setObjectName("cmd_save")
        self.verticalLayout.addWidget(self.cmd_save)
        self.cmd_cancel = QtWidgets.QPushButton(self.centralwidget)
        self.cmd_cancel.setObjectName("cmd_cancel")
        self.verticalLayout.addWidget(self.cmd_cancel)
        self.horizontalLayout_4.addLayout(self.verticalLayout)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gv_xy = GraphicsView(self.centralwidget)
        self.gv_xy.setAutoFillBackground(False)
        self.gv_xy.setStyleSheet("")
        self.gv_xy.setObjectName("gv_xy")
        self.gridLayout_2.addWidget(self.gv_xy, 0, 0, 1, 1)
        self.gv_xz = GraphicsView(self.centralwidget)
        self.gv_xz.setAutoFillBackground(False)
        self.gv_xz.setStyleSheet("")
        self.gv_xz.setObjectName("gv_xz")
        self.gridLayout_2.addWidget(self.gv_xz, 0, 1, 1, 1)
        self.gv_yz = GraphicsView(self.centralwidget)
        self.gv_yz.setAutoFillBackground(False)
        self.gv_yz.setStyleSheet("")
        self.gv_yz.setObjectName("gv_yz")
        self.gridLayout_2.addWidget(self.gv_yz, 1, 0, 1, 1)
        self.horizontalLayout_4.addLayout(self.gridLayout_2)
        self.horizontalLayout_4.setStretch(1, 1)
        Converter.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Converter)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1004, 20))
        self.menubar.setObjectName("menubar")
        Converter.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Converter)
        self.statusbar.setObjectName("statusbar")
        Converter.setStatusBar(self.statusbar)

        self.retranslateUi(Converter)
        QtCore.QMetaObject.connectSlotsByName(Converter)

    def retranslateUi(self, Converter):
        _translate = QtCore.QCoreApplication.translate
        Converter.setWindowTitle(_translate("Converter", "Convert to reciprocal space"))
        self.label_6.setText(_translate("Converter", "ROI to process:"))
        self.groupBox.setTitle(_translate("Converter", "Experiment geometry"))
        self.chk_omega.setText(_translate("Converter", "Omega"))
        self.chk_chi.setText(_translate("Converter", "Chi"))
        self.chk_mu.setText(_translate("Converter", "Mu"))
        self.chk_phi.setText(_translate("Converter", "Phi"))
        self.chk_omega_t.setText(_translate("Converter", "Omega_t"))
        self.label.setText(_translate("Converter", "Beam energy:"))
        self.label_7.setText(_translate("Converter", "Detector rotation"))
        self.cmb_detector_rotation.setItemText(0, _translate("Converter", "Vertical"))
        self.cmb_detector_rotation.setItemText(1, _translate("Converter", "Horizontal"))
        self.groupBox_2.setTitle(_translate("Converter", "Center pixel:"))
        self.label_2.setText(_translate("Converter", "X:"))
        self.label_3.setText(_translate("Converter", "Y:"))
        self.groupBox_3.setTitle(_translate("Converter", "Pixel size, um:"))
        self.label_4.setText(_translate("Converter", "X:"))
        self.label_5.setText(_translate("Converter", "Y:"))
        self.groupBox_5.setTitle(_translate("Converter", "Detector position:"))
        self.label_9.setText(_translate("Converter", "Dictance:"))
        self.label_8.setText(_translate("Converter", "Rotation:"))
        self.label_10.setText(_translate("Converter", "Tilt azimuth:"))
        self.label_11.setText(_translate("Converter", "Tilt:"))
        self.groupBox_6.setTitle(_translate("Converter", "Shifts:"))
        self.label_12.setText(_translate("Converter", "Omega"))
        self.label_13.setText(_translate("Converter", "Chi"))
        self.label_14.setText(_translate("Converter", "Phi"))
        self.label_15.setText(_translate("Converter", "Gamma"))
        self.label_16.setText(_translate("Converter", "Delta"))
        self.groupBox_7.setTitle(_translate("Converter", "Bins:"))
        self.label_17.setText(_translate("Converter", "X:"))
        self.label_18.setText(_translate("Converter", "Y:"))
        self.label_19.setText(_translate("Converter", "Z:"))
        self.cmd_preview.setText(_translate("Converter", "Preview"))
        self.cmd_save.setText(_translate("Converter", "Save"))
        self.cmd_cancel.setText(_translate("Converter", "Cancel"))

from pyqtgraph import GraphicsView
