import sys
import os

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QWidget, QLabel, QSlider, QSpinBox, QCheckBox, QPushButton
import cv2.cv2 as cv2
import numpy as np

import QSS
import Functions

loaded_image = np.empty(0)
manipulated_image = np.empty(0)
preview_image = np.empty(0)
image_history = []
image_history_index = -1

main_window = None

save_location = None

SCREEN_MULTIPLIER = 0.45
IMAGE_WIDTH, IMAGE_HEIGHT = 800, 800
MENU_BAR_HEIGHT = 36


class CheckBox(QCheckBox):
    def __init__(self, init_val, parent=None):
        super().__init__(parent)
        self.init_val = init_val
        self.stateChanged.connect(lambda: self.valueChange())

    def valueChange(self):
        self.parent().drawPreviewImage()


class SpinBox(QSpinBox):
    def __init__(self, init_val, parent=None):
        super().__init__(parent)

        self.init_val = init_val
        self.valueChanged.connect(lambda: self.valueChange())

    def valueChange(self):
        if self.parent().slider is not None:
            a = (self.value() - self.init_val) % self.singleStep()
            self.blockSignals(True)
            self.setValue(self.value() - a)
            self.blockSignals(False)
            self.parent().slider.blockSignals(True)
            self.parent().slider.setValue(self.value())
            self.parent().slider.blockSignals(False)

            self.parent().drawPreviewImage()


class Slider(QSlider):
    def __init__(self, init_val, orientation=None, parent=None):
        super().__init__(orientation, parent)

        self.init_val = init_val
        self.valueChanged.connect(lambda: self.valueChange())

    def valueChange(self):
        if self.parent().spin_box is not None:
            a = (self.value() - self.init_val) % self.singleStep()
            self.blockSignals(True)
            self.setValue(self.value() - a)
            self.blockSignals(False)
            self.parent().spin_box.blockSignals(True)
            self.parent().spin_box.setValue(self.value())
            self.parent().spin_box.blockSignals(False)

            self.parent().drawPreviewImage()


class Field(QLabel):
    def __init__(self, field_name, init_val, min_val, max_val, step_size, parent=None):
        super().__init__(parent)
        self.text = None
        self.spin_box = None
        self.slider = None
        self.check_box = None
        self.value_look_up = None
        self.init_val = init_val
        self.min_val = min_val
        self.max_val = max_val
        self.step_size = step_size

        self.text = QLabel(self)
        self.text.setText('{}:'.format(field_name))
        self.text.setAccessibleName('text_field')

        if self.min_val == 0 and self.max_val == 1:
            self.check_box = CheckBox(self.init_val, self)
            self.value_look_up = self.check_box
        else:
            self.spin_box = SpinBox(self.init_val, self)
            self.slider = Slider(self.init_val, Qt.Horizontal, self)
            self.value_look_up = self.spin_box
        self.setInitialValuesAndRange()

    def setInitialValuesAndRange(self):
        if self.min_val == 0 and self.max_val == 1:
            self.check_box.setChecked(self.init_val)
        else:
            self.spin_box.blockSignals(True)
            self.spin_box.setRange(self.min_val, self.max_val)
            self.spin_box.setValue(self.init_val)
            self.spin_box.blockSignals(False)

            self.spin_box.setSingleStep(self.step_size)
            self.spin_box.setKeyboardTracking(False)

            self.slider.blockSignals(True)
            self.slider.setRange(self.min_val, self.max_val)
            self.slider.setValue(self.init_val)
            self.slider.blockSignals(False)

            self.slider.setTickInterval(self.step_size)
            self.slider.setTickPosition(QSlider.TicksBelow)
            self.slider.setSingleStep(self.step_size)

    def returnLookUpValue(self):
        if self.min_val == 0 and self.max_val == 1:
            return self.value_look_up.isChecked()
        else:
            return self.value_look_up.value()

    def drawElements(self):
        self.text.setGeometry(0, 0, self.width() // 2, self.height() // 2)
        if self.min_val == 0 and self.max_val == 1:
            self.check_box.setGeometry(self.width() - self.check_box.width(), 0, self.width() // 2, self.height() // 2)
        else:
            self.spin_box.setGeometry(self.width() // 2, 0, self.width() // 2, self.height() // 2)
            self.slider.setGeometry(0, self.height() // 2, self.width(), self.height() // 2)

    def updateAll(self, value):
        self.spin_box.setValue(self.init_val)
        self.spin_box.setDisabled(not value)
        self.slider.setValue(self.init_val)
        self.slider.setDisabled(not value)

    def drawPreviewImage(self):
        self.parent().drawPreviewImage()


class MovablePreview(QLabel):
    def __init__(self, image_data, parent=None):
        super().__init__(parent)

        self.oldPos = self.pos()

        self.image_data_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        self.image = QtGui.QImage(self.image_data_rgb, self.image_data_rgb.shape[1], self.image_data_rgb.shape[0], self.image_data_rgb.strides[0], QtGui.QImage.Format_RGB888)

        self.preview_image = QLabel(self)
        self.preview_image.setGeometry(0, 0, self.image.width(), self.image.height())
        self.drawPreviewImage()

        self.setCursor(QCursor(Qt.OpenHandCursor))

    def changePreviewImage(self, image_data):
        if image_data.shape[0] == 0 or image_data.shape[1] == 0:
            self.image_data_rgb = image_data
        else:
            self.image_data_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        self.image = QtGui.QImage(self.image_data_rgb, self.image_data_rgb.shape[1], self.image_data_rgb.shape[0], self.image_data_rgb.strides[0], QtGui.QImage.Format_RGB888)
        self.drawPreviewImage()

    def drawPreviewImage(self):
        self.preview_image.setGeometry(self.preview_image.x(), self.preview_image.y(), self.image.width(), self.image.height())
        new_x, new_y = self.preview_image.x(), self.preview_image.y()
        if self.image.width() > self.width():
            new_x = clamp(self.preview_image.x(), -self.image.width() + self.width(), 0)
        if self.image.height() > self.height():
            new_y = clamp(self.preview_image.y(), -self.image.height() + self.height(), 0)
        self.preview_image.move(new_x, new_y)
        self.preview_image.setPixmap(QtGui.QPixmap.fromImage(self.image))

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
        self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        new_x, new_y = self.preview_image.x(), self.preview_image.y()
        if self.image.width() > self.width():
            new_x = clamp(self.preview_image.x() + delta.x(), -self.image.width() + self.width(), 0)
        if self.image.height() > self.height():
            new_y = clamp(self.preview_image.y() + delta.y(), -self.image.height() + self.height(), 0)
        self.preview_image.move(new_x, new_y)
        self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.setCursor(QCursor(Qt.OpenHandCursor))


class AnotherWindow(QWidget):
    def __init__(self, title, function, image_data, basic_fields=None, advanced_fields=None):
        if basic_fields is None:
            basic_fields = []
        if advanced_fields is None:
            advanced_fields = []
        super().__init__()

        self.function = function
        self.basic_fields = []
        self.advanced_fields = []

        length = max(len(advanced_fields) + len(basic_fields), 2)
        self.setFixedSize(IMAGE_WIDTH, self.height() // 20 + 3 * IMAGE_WIDTH // 20 * length + IMAGE_WIDTH // 8)
        self.setWindowTitle(title)

        self.preview = MovablePreview(image_data, self)
        self.preview.setGeometry(self.width() // 40, self.height() // 40, self.width() // 2, 3 * IMAGE_WIDTH // 20 * length + IMAGE_WIDTH // 40)

        for field_ind, field in enumerate(basic_fields):
            field_name, init_val, min_val, max_val, step_size = field
            new_field = Field(field_name, init_val, min_val, max_val, step_size, self)
            self.basic_fields.append(new_field)
            new_field.setGeometry(11 * self.width() // 20, self.height() // 40 + 3 * IMAGE_WIDTH // 20 * field_ind, 17 * self.width() // 40, IMAGE_WIDTH // 10)
            new_field.drawElements()

        if len(advanced_fields) > 0:
            self.enable_advanced_option = QCheckBox('Enable Advanced Options', self)
            self.enable_advanced_option.setGeometry(11 * self.width() // 20, self.height() // 40 + 3 * IMAGE_WIDTH // 20 * len(basic_fields), 17 * self.width() // 40, IMAGE_WIDTH // 40)
            self.enable_advanced_option.stateChanged.connect(lambda: self.updateAll(self.enable_advanced_option.isChecked()))

        for field_ind in range(len(advanced_fields)):
            field = advanced_fields[field_ind]
            field_name, init_val, min_val, max_val, step_size = field
            new_field = Field(field_name, init_val, min_val, max_val, step_size, self)
            self.advanced_fields.append(new_field)
            new_field.setGeometry(11 * self.width() // 20, self.height() // 40 + 3 * IMAGE_WIDTH // 20 * (field_ind + len(basic_fields)) + 3 * IMAGE_WIDTH // 40, 17 * self.width() // 40,
                                  IMAGE_WIDTH // 10)
            new_field.drawElements()
            new_field.updateAll(False)

        self.apply_button = QPushButton('Apply', self)
        self.apply_button.setGeometry(self.width() // 8, self.height() // 40 + 3 * IMAGE_WIDTH // 20 * length + IMAGE_WIDTH // 10 - self.height() // 10, self.width() // 4, IMAGE_WIDTH // 20)
        self.apply_button.pressed.connect(lambda: self.pressedOK())

        self.cancel_Button = QPushButton('Cancel', self)
        self.cancel_Button.setGeometry(5 * self.width() // 8, self.height() // 40 + 3 * IMAGE_WIDTH // 20 * length + IMAGE_WIDTH // 10 - self.height() // 10, self.width() // 4, IMAGE_WIDTH // 20)
        self.cancel_Button.pressed.connect(lambda: self.pressedCancel())

        self.drawPreviewImage()

    def drawPreviewImage(self):
        global preview_image

        args = []
        for basic_field in self.basic_fields:
            args.append(basic_field.returnLookUpValue())
        for advanced_field in self.advanced_fields:
            args.append(advanced_field.returnLookUpValue())
        new_image_data = self.function(manipulated_image, args)
        preview_image = new_image_data
        self.preview.changePreviewImage(new_image_data)

    def pressedOK(self):
        global manipulated_image, image_history, image_history_index

        manipulated_image = preview_image
        main_window.drawManipulatedImage(manipulated_image)
        main_window.updateAllActions(True)
        image_history_index += 1
        image_history.insert(image_history_index, manipulated_image)
        image_history = image_history[:image_history_index + 1]
        self.close()

    def pressedCancel(self):
        main_window.updateAllActions(True)
        self.close()

    def updateAll(self, value):
        for field in self.advanced_fields:
            field.updateAll(value)

    def closeEvent(self, event):
        self.pressedCancel()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)

        self.oldPos = self.pos()
        self.actions_dict = {}
        self.nonImageActions_dict = {}

        self.start_text = QLabel(self)
        self.start_text.setGeometry(self.width() // 40, self.width() // 40 + MENU_BAR_HEIGHT, 2 * IMAGE_WIDTH - self.width() // 20, IMAGE_HEIGHT - self.width() // 20)
        self.start_text.setText('Drag and Drop Images or File/Open... to Get Started!')
        self.start_text.setAccessibleName('start_text')
        self.start_text.setAlignment(Qt.AlignCenter)

        self.loaded_image_frame = QLabel(self)
        self.loaded_image_frame.setGeometry(0, MENU_BAR_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
        self.loaded_image_frame.setAccessibleName('loaded_image_frame')

        self.manipulated_image_frame = QLabel(self)
        self.manipulated_image_frame.setGeometry(IMAGE_WIDTH, MENU_BAR_HEIGHT, IMAGE_WIDTH, IMAGE_HEIGHT)
        self.manipulated_image_frame.setAccessibleName('manipulated_image_frame')

        self.window = None

        self._createActions()
        self._createMenuBar()

    def _createActions(self):
        self.minimize_action = QAction('&Minimize', self)
        self.minimize_action.triggered.connect(lambda: main_window.showMinimized())
        self.actions_dict['minimize_action'] = self.minimize_action
        self.nonImageActions_dict['minimize_action'] = self.minimize_action
        self.close_action = QAction('&Close', self)
        self.close_action.triggered.connect(lambda: sys.exit())
        self.actions_dict['close_action'] = self.close_action
        self.nonImageActions_dict['close_action'] = self.close_action

        self.open_action = QAction('&Open...', self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.triggered.connect(open_file_action)
        self.actions_dict['open_action'] = self.open_action
        self.nonImageActions_dict['open_action'] = self.open_action
        self.save_action = QAction('&Save', self)
        self.save_action.setShortcut('Ctrl+S')
        self.save_action.triggered.connect(save_file_action)
        self.actions_dict['save_action'] = self.save_action
        self.save_as_action = QAction('Save &As...', self)
        self.save_as_action.setShortcut('Shift+Ctrl+S')
        self.save_as_action.triggered.connect(save_as_file_action)
        self.actions_dict['save_as_action'] = self.save_as_action
        self.reset_action = QAction('&Reset', self)
        self.reset_action.setShortcut('Ctrl+R')
        self.reset_action.triggered.connect(reset_image_action)
        self.actions_dict['reset_action'] = self.reset_action
        self.undo_action = QAction('&Undo', self)
        self.undo_action.setShortcut('Ctrl+Z')
        self.undo_action.triggered.connect(undo_action)
        self.actions_dict['undo_action'] = self.undo_action
        self.redo_action = QAction('R&edo', self)
        self.redo_action.setShortcut('Ctrl+Y')
        self.redo_action.triggered.connect(redo_action)
        self.actions_dict['redo_action'] = self.redo_action
        self.exit_action = QAction('&Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.triggered.connect(lambda: sys.exit())
        self.actions_dict['exit_action'] = self.exit_action
        self.nonImageActions_dict['exit_action'] = self.exit_action

        self.box_blur_action = QAction('&Box Blur...', self)
        self.box_blur_action.triggered.connect(lambda: self.createNewWindow(
            'Box Blur',
            Functions.box_blur,
            manipulated_image,
            [('Kernel Size X', 1, 1, 49, 1),
             ('Kernel Size Y', 1, 1, 49, 1)]))
        self.actions_dict['box_blur_action'] = self.box_blur_action
        self.gaussian_blur_action = QAction('&Gaussian Blur...', self)
        self.gaussian_blur_action.triggered.connect(lambda: self.createNewWindow(
            'Gaussian Blur',
            Functions.gaussian_blur,
            manipulated_image,
            [('Kernel Size X', 1, 1, 49, 2),
             ('Kernel Size Y', 1, 1, 49, 2)],
            [('Std Deviation', 0, 0, 100, 1)]
        ))
        self.actions_dict['gaussian_blur_action'] = self.gaussian_blur_action
        self.median_blur_action = QAction('&Median Blur...', self)
        self.median_blur_action.triggered.connect(lambda: self.createNewWindow(
            'Median Blur',
            Functions.median_blur,
            manipulated_image,
            [('Kernel Size', 1, 1, 49, 2)]))
        self.actions_dict['median_blur_action'] = self.median_blur_action
        self.bilateral_blur_action = QAction('B&ilateral Blur...', self)
        self.bilateral_blur_action.triggered.connect(lambda: self.createNewWindow(
            'Bilateral Blur',
            Functions.bilateral_blur,
            manipulated_image,
            [('Kernel Size', 1, 1, 19, 1)],
            [('Sigma Color', 0, 0, 300, 5),
             ('Sigma Space', 0, 0, 300, 5)]
        ))
        self.actions_dict['bilateral_blur_action'] = self.bilateral_blur_action
        self.remove_blur_action = QAction('&Remove Blur', self)
        self.remove_blur_action.triggered.connect(lambda: remove_blur_action())
        self.actions_dict['remove_blur_action'] = self.remove_blur_action

        self.crop_action = QAction('&Crop...', self)
        self.crop_action.triggered.connect(lambda: self.createNewWindow(
            'Crop',
            Functions.crop_image,
            manipulated_image,
            [('X1', 0, 0, manipulated_image.shape[1], 1),
             ('X2', manipulated_image.shape[1], 2, manipulated_image.shape[1], 1),
             ('Y1', 0, 0, manipulated_image.shape[0], 1),
             ('Y2', manipulated_image.shape[0], 2, manipulated_image.shape[0], 1)]
        ))
        self.actions_dict['crop_action'] = self.crop_action
        self.flip_action = QAction('&Flip...', self)
        self.flip_action.triggered.connect(lambda: self.createNewWindow(
            'Flip',
            Functions.flip_image,
            manipulated_image,
            [('Flip Horizontal', False, 0, 1, 1),
             ('Flip Vertical', False, 0, 1, 1)]
        ))
        self.actions_dict['flip_action'] = self.flip_action
        self.mirror_action = QAction('&Mirror...', self)
        self.mirror_action.triggered.connect(lambda: self.createNewWindow(
            'Mirror',
            Functions.mirror_image,
            manipulated_image,
            [('Mirror Horizontal', False, 0, 1, 1),
             ('Mirror Vertical', False, 0, 1, 1)]
        ))
        self.actions_dict['mirror_action'] = self.mirror_action
        self.rotate_action = QAction('&Rotate...', self)
        self.rotate_action.triggered.connect(lambda: main_window.createNewWindow(
            'Rotate',
            Functions.rotate_image,
            manipulated_image,
            [('Rotation Angle', 0, 0, 359, 1)],
            [('Rotation Center X', manipulated_image.shape[1] // 2, 0, manipulated_image.shape[1], 1),
             ('Rotation Center Y', manipulated_image.shape[0] // 2, 0, manipulated_image.shape[0], 1)]
        ))
        self.actions_dict['rotate_action'] = self.rotate_action
        self.reverse_action = QAction('&Negative', self)
        self.reverse_action.triggered.connect(lambda: reverse_action())
        self.actions_dict['reverse_action'] = self.reverse_action

        self.grayscale_action = QAction('&Convert to Grayscale', self)
        self.grayscale_action.triggered.connect(lambda: grayscale_action())
        self.actions_dict['grayscale_action'] = self.grayscale_action
        self.color_balance_action = QAction('C&hange Color Balance...', self)
        self.color_balance_action.triggered.connect(lambda: main_window.createNewWindow(
            'Change Color Balance',
            Functions.change_color_balance,
            manipulated_image,
            [('Channel', 0, 0, 2, 1),
             ('Amount', 0, -255, 255, 1)]
        ))
        self.actions_dict['color_balance_action'] = self.color_balance_action
        self.color_brightness_action = QAction('Ch&ange Contrast and Brightness...', self)
        self.color_brightness_action.triggered.connect(lambda: main_window.createNewWindow(
            'Change Contrast and Brightness',
            Functions.change_contrast_and_brightness,
            manipulated_image,
            [('Alpha', 10, 0, 100, 1),
             ('Beta', 0, -255, 255, 1)],
            [('Gamma', 10, 0, 100, 1)]
        ))
        self.actions_dict['color_brightness_action'] = self.color_brightness_action

        self.salt_and_pepper_noise_action = QAction('&Salt and Pepper...', self)
        self.salt_and_pepper_noise_action.triggered.connect(lambda: self.createNewWindow(
            'Salt and Pepper Noise',
            Functions.salt_and_pepper_noise,
            manipulated_image,
            [('Salt Vs Pepper(%)', 50, 0, 100, 1),
             ('Amount(%)', 5, 0, 100, 1)]
        ))
        self.actions_dict['salt_and_pepper_noise_action'] = self.salt_and_pepper_noise_action
        self.gaussian_noise_action = QAction('&Gaussian Noise...', self)
        self.gaussian_noise_action.triggered.connect(lambda: self.createNewWindow(
            'Gaussian Noise',
            Functions.gaussian_noise,
            manipulated_image,
            [('Mean', 0, 0, 100, 1),
             ('Variance', 0, 0, 100, 1)]
        ))
        self.actions_dict['gaussian_noise_action'] = self.gaussian_noise_action
        self.poisson_noise_action = QAction('&Poisson Noise', self)
        self.poisson_noise_action.triggered.connect(lambda: poisson_noise_action())
        self.actions_dict['poisson_noise_action'] = self.poisson_noise_action
        self.speckle_noise_action = QAction('S&peckle Noise...', self)
        self.speckle_noise_action.triggered.connect(lambda: self.createNewWindow(
            'Speckle Noise',
            Functions.speckle_noise,
            manipulated_image,
            [('Mean', 0, 0, 100, 1),
             ('Variance', 0, 0, 100, 1)]
        ))
        self.actions_dict['speckle_noise_action'] = self.speckle_noise_action

        self.naive_edge_detect_action = QAction('&Naive Edge Detection', self)
        self.naive_edge_detect_action.triggered.connect(lambda: naive_edge_detection_action())
        self.actions_dict['naive_edge_detect_action'] = self.naive_edge_detect_action
        self.sobel_edge_detect_action = QAction('&Sobel Edge Detection...', self)
        self.sobel_edge_detect_action.triggered.connect(lambda: sobel_edge_detection_action())
        self.actions_dict['sobel_edge_detect_action'] = self.sobel_edge_detect_action
        self.canny_edge_detect_action = QAction('&Canny Edge Detection...', self)
        self.canny_edge_detect_action.triggered.connect(lambda: canny_edge_detection_action())
        self.actions_dict['canny_edge_detect_action'] = self.canny_edge_detect_action

        self.help_action = QAction('&Help...', self)
        # self.help_action.triggered.connect()
        self.actions_dict['help_action'] = self.help_action
        self.nonImageActions_dict['help_action'] = self.help_action
        self.about_action = QAction('&About [INSERT NAME HERE]...', self)
        # self.about_action.triggered.connect()
        self.actions_dict['about_action'] = self.about_action
        self.nonImageActions_dict['about_action'] = self.about_action

        self.updateAllImageActions(False)

    def _createMenuBar(self):
        menu_bar = self.menuBar()

        logo_menu = menu_bar.addMenu(QIcon('../resources/PixoLogo.png'), '&Pixo')
        logo_menu.addActions((self.minimize_action,
                              self.close_action))

        file_menu = menu_bar.addMenu('&File')
        file_menu.addActions((self.open_action,
                              self.save_action,
                              self.save_as_action,
                              file_menu.addSeparator(),
                              self.reset_action,
                              self.undo_action,
                              self.redo_action,
                              file_menu.addSeparator(),
                              self.exit_action))

        edit_menu = menu_bar.addMenu('&Edit')

        blur_menu = edit_menu.addMenu('&Blur')
        blur_menu.addActions((self.box_blur_action,
                              self.gaussian_blur_action,
                              self.median_blur_action,
                              self.bilateral_blur_action,
                              self.remove_blur_action))
        edit_menu.addSeparator()

        orientation_menu = edit_menu.addMenu('&Orientation')
        orientation_menu.addActions((self.crop_action,
                                     self.flip_action,
                                     self.mirror_action,
                                     self.rotate_action,
                                     self.reverse_action))
        edit_menu.addSeparator()

        color_menu = edit_menu.addMenu('&Color')
        color_menu.addActions((self.grayscale_action,
                               self.color_balance_action,
                               self.color_brightness_action))
        edit_menu.addSeparator()

        noise_menu = edit_menu.addMenu('&Noise')
        noise_menu.addActions((self.salt_and_pepper_noise_action,
                               self.gaussian_noise_action,
                               self.poisson_noise_action,
                               self.speckle_noise_action))
        edit_menu.addSeparator()

        detect_edge_menu = edit_menu.addMenu('&Edge Detection')
        detect_edge_menu.addActions((self.naive_edge_detect_action,
                                     self.sobel_edge_detect_action,
                                     self.canny_edge_detect_action))

        help_menu = menu_bar.addMenu('&Help')
        help_menu.addActions((self.help_action,
                              file_menu.addSeparator(),
                              self.about_action))

    def updateAllActions(self, value):
        for key, val in self.actions_dict.items():
            val.setEnabled(value)
        if isGrayscale(manipulated_image):
            self.updateActionAbility(['grayscale_action', 'color_balance_action'], [False, False])

    def updateAllImageActions(self, value):
        for key, val in self.actions_dict.items():
            if key not in self.nonImageActions_dict:
                val.setEnabled(value)

    def updateActionAbility(self, actions, values):
        for ind, act in enumerate(actions):
            self.actions_dict[act].setEnabled(values[ind])

    def drawLoadedImage(self, image_data):
        aspect_ratio = image_data.shape[1] / image_data.shape[0]
        new_width, new_height = IMAGE_WIDTH, int(IMAGE_WIDTH / aspect_ratio)
        image_data_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        image_data_rgb = cv2.resize(image_data_rgb, (new_width, new_height))
        image = QtGui.QImage(image_data_rgb, image_data_rgb.shape[1], image_data_rgb.shape[0], image_data_rgb.strides[0], QtGui.QImage.Format_RGB888)
        self.loaded_image_frame.setPixmap(QtGui.QPixmap.fromImage(image))
        self.updateLoadedFrameHeight(new_height)
        self.updateMainWindowHeight()

    def drawManipulatedImage(self, image_data):
        aspect_ratio = image_data.shape[1] / image_data.shape[0]
        new_width, new_height = IMAGE_WIDTH, int(IMAGE_WIDTH / aspect_ratio)
        image_data_rgb = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        image_data_rgb = cv2.resize(image_data_rgb, (new_width, new_height))
        image = QtGui.QImage(image_data_rgb, image_data_rgb.shape[1], image_data_rgb.shape[0], image_data_rgb.strides[0], QtGui.QImage.Format_RGB888)
        self.manipulated_image_frame.setPixmap(QtGui.QPixmap.fromImage(image))
        self.updateManipulatedFrameHeight(new_height)
        self.updateMainWindowHeight()

    def updateLoadedFrameHeight(self, height):
        self.loaded_image_frame.setGeometry(0, MENU_BAR_HEIGHT, IMAGE_WIDTH, height)

    def updateManipulatedFrameHeight(self, height):
        self.manipulated_image_frame.setGeometry(IMAGE_WIDTH, MENU_BAR_HEIGHT, IMAGE_WIDTH, height)

    def updateMainWindowHeight(self):
        self.setFixedSize(2 * IMAGE_WIDTH, max(self.loaded_image_frame.height(), self.manipulated_image_frame.height()))

    def createNewWindow(self, title, function, image_data, basic_fields=None, advanced_fields=None):
        if basic_fields is None:
            basic_fields = []
        if advanced_fields is None:
            advanced_fields = []
        self.window = AnotherWindow(title, function, image_data, basic_fields, advanced_fields)
        self.window.show()
        self.updateAllActions(False)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def dragEnterEvent(self, event):
        file_name, file_extension = os.path.splitext(event.mimeData().urls()[0].toLocalFile())
        if file_extension in ('.png', '.jpg', '.jpeg'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        file_name, file_extension = os.path.splitext(event.mimeData().urls()[0].toLocalFile())
        if file_extension in ('.png', '.jpg', '.jpeg'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_name, file_extension = os.path.splitext(event.mimeData().urls()[0].toLocalFile())
        if file_extension in ('.png', '.jpg', '.jpeg'):
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            open_file(file_path)
            event.accept()
        else:
            event.ignore()


def open_file_action():
    name = QFileDialog.getOpenFileName(caption='Open', filter='Image Files (*.png *.jpg *.jpeg)')
    if name[0] != '':
        open_file(name[0])


def open_file(path):
    global main_window, loaded_image, manipulated_image, image_history, image_history_index

    loaded_image = cv2.imread(path)
    manipulated_image = np.copy(loaded_image)
    main_window.updateAllImageActions(True)
    main_window.drawLoadedImage(loaded_image)
    main_window.drawManipulatedImage(manipulated_image)
    image_history = [manipulated_image]
    image_history_index = 0
    main_window.start_text.setVisible(False)

    if isGrayscale(loaded_image):
        main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [False, False])


def reset_image_action():
    global loaded_image, manipulated_image, image_history, image_history_index

    if not np.array_equal(loaded_image, manipulated_image):
        manipulated_image = loaded_image
        main_window.drawManipulatedImage(manipulated_image)
        main_window.updateAllActions(True)
        image_history_index += 1
        image_history.insert(image_history_index, manipulated_image)
        image_history = image_history[:image_history_index + 1]


def undo_action():
    global image_history, image_history_index, manipulated_image

    if image_history_index > 0:
        image_history_index -= 1
        manipulated_image = image_history[image_history_index]
        main_window.drawManipulatedImage(manipulated_image)
        if isGrayscale(manipulated_image):
            main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [False, False])
        else:
            main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [True, True])


def redo_action():
    global image_history, image_history_index, manipulated_image

    if image_history_index < len(image_history) - 1:
        image_history_index += 1
        print('1')
        manipulated_image = image_history[image_history_index]
        print('2')
        main_window.drawManipulatedImage(manipulated_image)
        print('3')
        if isGrayscale(manipulated_image):
            print('4')
            main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [False, False])
            print('5')
        else:
            print('6')
            main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [True, True])
            print('7')


def save_file_action():
    global save_location

    if save_location is not None:
        cv2.imwrite(save_location, manipulated_image)
    else:
        name = QFileDialog.getSaveFileName(caption='Save', filter='Image Files (*.png *.jpg *.jpeg)')
        if name[0] != '':
            save_location = name[0]
            cv2.imwrite(name[0], manipulated_image)


def save_as_file_action():
    name = QFileDialog.getSaveFileName(caption='Save', filter='Image Files (*.png *.jpg *.jpeg)')
    if name[0] != '':
        cv2.imwrite(name[0], manipulated_image)


def remove_blur_action():
    global manipulated_image

    manipulated_image = Functions.de_blur(manipulated_image)
    main_window.drawManipulatedImage(manipulated_image)


def reverse_action():
    global manipulated_image

    manipulated_image = Functions.reverse_image(manipulated_image)
    main_window.drawManipulatedImage(manipulated_image)


def grayscale_action():
    global manipulated_image, image_history, image_history_index

    manipulated_image = Functions.grayscale_image(manipulated_image)
    main_window.drawManipulatedImage(manipulated_image)
    main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [False, False])
    image_history_index += 1
    image_history.insert(image_history_index, manipulated_image)
    image_history = image_history[:image_history_index + 1]


def poisson_noise_action():
    global manipulated_image, image_history, image_history_index

    manipulated_image = Functions.poisson_noise(manipulated_image)
    main_window.drawManipulatedImage(manipulated_image)
    image_history_index += 1
    image_history.insert(image_history_index, manipulated_image)
    image_history = image_history[:image_history_index + 1]


def naive_edge_detection_action():
    global manipulated_image, image_history, image_history_index

    manipulated_image = Functions.naive_edge_detect(manipulated_image)
    main_window.drawManipulatedImage(manipulated_image)
    main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [False, False])
    image_history_index += 1
    image_history.insert(image_history_index, manipulated_image)
    image_history = image_history[:image_history_index + 1]


def sobel_edge_detection_action():
    main_window.createNewWindow(
        'Sobel Edge Detection',
        Functions.sobel_edge_detect,
        manipulated_image,
        [('Kernel Size', 1, 1, 7, 2)],
        [('dX', 1, 0, 2, 1),
         ('dY', 1, 0, 2, 1)]
    )
    main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [False, False])


def canny_edge_detection_action():
    main_window.createNewWindow(
        'Canny Edge Detection',
        Functions.canny_edge_detect,
        manipulated_image,
        [('Threshold 1', 0, 0, 1000, 1),
         ('Threshold 2', 0, 0, 1000, 1)]
    )
    main_window.updateActionAbility(['grayscale_action', 'color_balance_action'], [False, False])


def clamp(x, m, M):
    return max(min(x, M), m)


def isGrayscale(image):
    if len(image.shape) == 3 and (image[:, :, 0] == image[:, :, 1]).all() and (image[:, :, 0] == image[:, :, 2]).all():
        return True
    return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS.qss)

    screen_width = QApplication.primaryScreen().size().width()
    screen_height = QApplication.primaryScreen().size().height()
    IMAGE_WIDTH = int(screen_width * SCREEN_MULTIPLIER)
    IMAGE_HEIGHT = int(screen_width * SCREEN_MULTIPLIER)

    main_window = MainWindow()
    main_window.setWindowFlag(Qt.FramelessWindowHint)
    main_window.setFixedSize(2 * IMAGE_WIDTH, IMAGE_HEIGHT + MENU_BAR_HEIGHT)
    main_window.move((screen_width - 2 * IMAGE_WIDTH) // 2, (screen_height - IMAGE_HEIGHT) // 2)
    main_window.setWindowTitle('[INSERT NAME HERE]')

    main_window.show()
    sys.exit(app.exec_())
