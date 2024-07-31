import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QWidget, QTextEdit, QLabel
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5 import uic, QtCore, QtOpenGL
from PyQt5.QtCore import Qt
from PIL import Image
import json

import moderngl
import numpy as np

import time
import datetime

form_class = uic.loadUiType("./src/UI/answer.ui")[0]

class AnswerWidget(QWidget, form_class):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        
        self.parent = parent
        
        self.window_pos_x = 30
        self.window_pos_y = 120
        self.window_width = 720
        self.window_height = 720
        
        self.isFinished = False
        
        self.init_ui()
        
        self.data_length = self.parent.data_length
        self.answer = self.parent.test_tab.answer
        self.boxes = {}
        
        self.controlBoxes = []
        self.controlPoints = []
        
        self.data = []
        
        self.data = self.parent.data
        
        self.gt = []
            
        with open('answer.json', 'r') as f:
            self.gt_full = json.load(f)
        for data_name in self.parent.data_list:
            self.gt.append(self.gt_full[data_name])
                    
        self.renderWindow.data = self.data[0]
        
        self.index: int = 0
        
        self.score_text = ''
        
        self.indexDisplay.append("image 1/" + str(self.data_length))
        self.reset_text()
        
        self.renderWindow.mouseDoubleClickEvent = self.add_control_box
        
        self.boxtexture = None
        
    def get_answer(self):
        self.answer = self.parent.test_tab.answer
        while True:
            if (self.index == self.data_length):
                self.index = 0
                self.finish()
                break
            if (self.answer[self.index][0] == 0):
                break
            self.index+=1
        self.renderWindow.data = self.data[self.index]
        self.reset_text()
        
    def reset_text(self):
        gt_text = ''
        if (self.isFinished):
            gt_text = "\nTrue Answer: " + self.data_to_text(self.gt[self.index])+ "\n" + self.score_text
            self.renderWindow.mouseDoubleClickEvent = None
        self.indexDisplay.setText("image " + str(self.index + 1) + "/" + str(self.data_length))
        # self.answerDisplay.setText("Your Answer: " + self.data_to_text(self.answer[self.index][0]) + gt_text)
        self.answerDisplay.setText("Your Answer: " + self.data_to_text(self.answer[self.index][0]) + gt_text )
        
    def data_to_text(self, data):
        if (data == 1):
            return "REAL"
        elif (data == 0):
            return "SYNTHETIC"
        else:
            return "UNDEFINED"
    
    def init_ui(self):
        self.nextButton.clicked.connect(self.next)
        self.prevButton.clicked.connect(self.prev)
        #self.saveButton.clicked.connect(self.save_data)
        #self.loadButton.clicked.connect(self.load_data)
        
        self.indexDisplay.setStyleSheet("font-size: 30px; font-weight: bold; border: 0;")
        self.answerDisplay.setStyleSheet("font-size: 30px; border: 0;")
        
        self.nextButton.setStyleSheet("background-color: #004191; color: white; font-size: 30px; font-weight: bold; border-radius: 10px;")
        self.prevButton.setStyleSheet("background-color: #004191; color: white; font-size: 30px; font-weight: bold; border-radius: 10px;")
        
        self.renderWindow = RenderWidget(self)
        self.renderWindow.setGeometry(self.window_pos_x, self.window_pos_y, self.window_width, self.window_height)
        
        self.before_button = QPushButton('본인이 합성이라고 생각한 이미지에서 왜 그렇게 생각하셨는지 체크해 주세요\n\nClick anywhere to continue', self)
        self.before_button.setGeometry(0, 0, 1300, 1000)
        self.before_button.setStyleSheet("background-color: white; color: black; font-size: 30px; font-weight: bold; border: 0;")
        self.before_button.clicked.connect(self.before_button_remove)
        
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.renderWindow.updateGL)
        self.timer.start()
        
        self.show()
        
    def before_button_remove(self):
        self.before_button.close()
        
    def after_button_remove(self):
        self.after_button.close()
    
    def select_real(self):
        self.answer[self.index][0] = 1
        self.answerDisplay.setText("Your Answer: REAL")
    
    def select_synth(self):
        self.answer[self.index][0] = 0
        self.answerDisplay.setText("Your Answer: SYNTHETIC")
    
    def prev(self):
        self.boxes[self.index] = self.controlBoxes
        self.parent.save_data()
        self.controlBoxes = []
        for cp in self.controlPoints:
            cp.close()
        
        now_index = self.index
        while True:
            self.index -= 1
            if (self.index == -1):
                if (self.isFinished):
                    self.index = self.data_length - 1
                else:
                    self.index = now_index
                    return
            if (self.isFinished):
                break
            if (self.answer[self.index][0] == 0):
                break
            
        self.renderWindow.data = self.data[self.index]
        self.indexDisplay.setText("image " + str(self.index + 1) + "/" + str(self.data_length))
        self.reset_text()
        
        if (self.index in self.boxes.keys() and self.boxes[self.index] is not None):
            self.controlBoxes = self.boxes[self.index]
            for cb in self.controlBoxes:
                self.make_control_points(cb)
            self.generateTexture()
        else:
            self.boxtexture = None
            self.renderWindow.box = np.zeros((240, 240, 4), dtype=np.float32)
    
    def next(self):
        self.boxes[self.index] = self.controlBoxes
        self.parent.save_data()
        self.controlBoxes = []
        for cp in self.controlPoints:
            cp.close()
        
        while True:
            self.index += 1
            if (self.index == self.data_length):
                self.index = 0
            if (self.index == self.data_length - 1):
                self.index = 0
                self.finish()
            if (self.isFinished):
                break
            if (self.answer[self.index][0] == 0):
                break
            
        self.renderWindow.data = self.data[self.index]
        self.indexDisplay.setText("image " + str(self.index + 1) + "/" + str(self.data_length))
        self.reset_text()
        
        if (self.index in self.boxes.keys() and self.boxes[self.index] is not None):
            self.controlBoxes = self.boxes[self.index]
            for cb in self.controlBoxes:
                self.make_control_points(cb)
            self.generateTexture()
        else:
            self.boxtexture = None
            self.renderWindow.box = np.zeros((240, 240, 4), dtype=np.float32)
            
    def finish(self):
        if (self.isFinished):
            return
        
        self.score_calculate()
        self.reset_text()
        
        
        self.after_button = QPushButton('Your ' + self.score_text + '\n\nClick anywhere to continue', self)
        self.after_button.setGeometry(0, 0, 1300, 1000)
        self.after_button.setStyleSheet("background-color: white; color: black; font-size: 30px; font-weight: bold; border: 0;")
        self.after_button.clicked.connect(self.after_button_remove)
        
        self.kaist_logo = QPixmap("./src/data/kaist_logo.png")
        self.cgv_logo = QPixmap("./src/data/cgv_logo.png")
        self.iitp_logo = QPixmap("./src/data/iitp_logo.png")
        
        self.kaist_logo = self.kaist_logo.scaledToHeight(100)
        self.cgv_logo = self.cgv_logo.scaledToHeight(100)
        self.iitp_logo = self.iitp_logo.scaledToHeight(100)
        
        self.kaist_label = QLabel(self.after_button)
        self.kaist_label.setPixmap(self.kaist_logo)
        self.kaist_label.setGeometry(100, 800, 400, 100)
        
        self.cgv_label = QLabel(self.after_button)
        self.cgv_label.setPixmap(self.cgv_logo)
        self.cgv_label.setGeometry(1000, 800, 200, 100)
        
        self.iitp_label = QLabel(self.after_button)
        self.iitp_label.setPixmap(self.iitp_logo)
        self.iitp_label.setGeometry(600, 800, 200, 100)
        
        self.isFinished = True
        
        self.after_button.show()
        
    def make_control_points(self, cb):
        clip = lambda x: max(min(x, 1), 0)
        x_min = clip(cb.x_min)
        x_max = clip(cb.x_max)
        y_min = clip(cb.y_min)
        y_max = clip(cb.y_max)
        x_min = self.window_pos_x + int(x_min * self.window_width)
        y_min = self.window_pos_y + int(y_min * self.window_height)
        x_max = self.window_pos_x + int(x_max * self.window_width)
        y_max = self.window_pos_y + int(y_max * self.window_height)
        
        button_ul = ControlPoint(self)
        button_ul.control_box = cb
        button_ul.button_type = 'ul'
        button_ul.setGeometry(x_min - 10, y_min - 10, 20, 20)
        button_ul.setStyleSheet('background-color: rgba(255, 255, 255, 120);')
        
        button_lr = ControlPoint(self)
        button_lr.control_box = cb
        button_lr.button_type = 'lr'
        button_lr.setGeometry(x_max - 10, y_max - 10, 20, 20)
        button_lr.setStyleSheet('background-color: rgba(255, 255, 255, 120);')
        button_lr.show()
        button_ul.show()
        button_lr.twin = button_ul
        button_ul.twin = button_lr
        self.controlPoints.append(button_lr)
        self.controlPoints.append(button_ul)
            
    def find_coltrol_box_idx(self, control_box):
        for i, cb in enumerate(self.controlBoxes):
            if (cb == control_box):
                return i
        return -1
    
    def add_control_box(self, e: QMouseEvent):
        x = e.x()
        y = e.y()
        width = 0.1
        height = 0.1
        cb = ControlBox()
        cb.x_min = (x / self.window_width - 0.5 * width)
        cb.x_max = (x / self.window_width + 0.5 * width)
        cb.y_min = (y / self.window_height) - 0.5 * height
        cb.y_max = (y / self.window_height) + 0.5 * height
        cb.r = 1.0
        cb.g = 1.0
        cb.b = 1.0
        cb.a = 1.0
        self.controlBoxes.append(cb)
        self.make_control_points(cb)
        self.generateTexture()
        
    def generateTexture(self):
        if (self.boxtexture is None):
            self.boxtexture = np.zeros((240, 240, 4), dtype=np.float32)
        self.boxtexture.fill(0.0)
        for controlBox in self.controlBoxes:
            x_min = int(controlBox.x_min * (240 - 1))
            x_max = int(controlBox.x_max * (240 - 1))
            y_min = int(controlBox.y_min * (240 - 1))
            y_max = int(controlBox.y_max * (240 - 1))
            self.boxtexture[y_min:y_min + 2, x_min:x_max] = np.array([controlBox.r, controlBox.g, controlBox.b, controlBox.a], dtype=np.float32)
            self.boxtexture[y_max - 2:y_max, x_min:x_max] = np.array([controlBox.r, controlBox.g, controlBox.b, controlBox.a], dtype=np.float32)
            self.boxtexture[y_min:y_max, x_min:x_min + 2] = np.array([controlBox.r, controlBox.g, controlBox.b, controlBox.a], dtype=np.float32)
            self.boxtexture[y_min:y_max, x_max - 2:x_max] = np.array([controlBox.r, controlBox.g, controlBox.b, controlBox.a], dtype=np.float32)
        self.renderWindow.box = self.boxtexture
        
    def get_data(self):
        data = {}
        for idx in range(self.data_length):
            cbs = []
            if (idx not in self.boxes.keys()):
                continue
            if (self.boxes[idx] is not None):
                for cb in self.boxes[idx]:
                    cbs.append({"x_min":cb.x_min, "x_max":cb.x_max, "y_min":cb.y_min, "y_max":cb.y_max, "comment":cb.comment})
            data[str(idx)] = cbs
        return data
    
    def score_calculate(self):
        score = 0
        for i,j in zip(self.answer, self.gt):   
            if i[0] == j:
                score += 1
        self.score_text = "Score: " + str(score) + "/" + str(self.data_length)

        return self.score_text
        
        
class ControlBox:
    def __init__(self) -> None:
        self.x_min: float = None
        self.x_max: float = None
        self.y_min: float = None
        self.y_max: float = None
        
        self.r: float = None
        self.g: float = None
        self.b: float = None
        self.a: float = None
        
        self.comment: str = ''
        
class ControlPoint(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.control_box = None
        self.button_type = None
        self.twin = None
        
    def mousePressEvent(self, e: QMouseEvent) -> None:
        self._mousePressPos = None
        self._mouseMovePos = None
        if e.button() == Qt.LeftButton:
            self._mousePressPos = e.globalPos()
            self._mouseMovePos = e.globalPos()
        elif e.button() == Qt.RightButton:
            self.remove_control_point()
        return super(ControlPoint, self).mousePressEvent(e)
    
    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        if (e.buttons() & Qt.LeftButton) and self._mousePressPos is not None:
            self.move(self.pos() + e.globalPos() - self._mouseMovePos)
            self._mouseMovePos = e.globalPos()
            x = self.x() + 5
            y = self.y() + 5
            # update tf
            if (self.button_type == 'ul'):
                tf_idx = self.parent.find_coltrol_box_idx(self.control_box)
                self.parent.controlBoxes[tf_idx].x_min = (x - self.parent.window_pos_x) / self.parent.window_width
                self.parent.controlBoxes[tf_idx].y_min = (y - self.parent.window_pos_y) / self.parent.window_height
            elif (self.button_type == 'lr'):
                tf_idx = self.parent.find_coltrol_box_idx(self.control_box)
                self.parent.controlBoxes[tf_idx].x_max = (x - self.parent.window_pos_x) / self.parent.window_width
                self.parent.controlBoxes[tf_idx].y_max = (y - self.parent.window_pos_y) / self.parent.window_height
            self.parent.generateTexture()
            
        return super(ControlPoint, self).mouseMoveEvent(e)
    
    def mouseDoubleClickEvent(self, a0: QMouseEvent) -> None:
        # self.parent.color_setting_dialog(self)
        self.commentWidget = CommentWidget(self.parent, self.control_box)
        return super().mouseDoubleClickEvent(a0)
    
    def remove_control_point(self):
        tf_idx = self.parent.find_coltrol_box_idx(self.control_box)
        self.parent.controlBoxes.pop(tf_idx)
        self.parent.controlPoints.remove(self)
        self.parent.controlPoints.remove(self.twin)
        self.parent.generateTexture()
        self.close()
        self.twin.close()
    
    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if (self._mousePressPos is not None):
            moved = self._mousePressPos - e.globalPos()
            if (moved.manhattanLength() <= 3):
                print('clicked')
            else:
                print('moved')
        return super(ControlPoint, self).mouseReleaseEvent(e)
    
class CommentWidget(QWidget):
    def __init__(self, parent, controlBox):
        super().__init__()
        self.parent = parent
        self.controlBox = controlBox
        self.initUI()
    
    def initUI(self):
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle('Comment')
        self.setStyleSheet("background-color: white;")
        
        self.commentText = QTextEdit(self)
        self.commentText.setGeometry(50, 50, 500, 200)
        self.commentText.setStyleSheet("border: 2px solid black;")
        self.commentText.setPlainText(self.controlBox.comment)
        
        self.applyButton = QPushButton('Apply', self)
        self.applyButton.setGeometry(250, 300, 100, 50)
        self.applyButton.setStyleSheet("background-color: #004191; color: white; font-size: 20px; font-weight: bold; border-radius: 10px;")
        
        self.applyButton.clicked.connect(self.apply)
        
        self.show()
        
    def get_comment(self):
        return self.commentText.toPlainText()
    
    def apply(self):
        self.controlBox.comment = self.get_comment()
        self.close()
    

    
class RenderWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super(RenderWidget, self).__init__(parent)
        
        self.box = np.zeros((240, 240, 4), dtype=np.float32)
        self.data = np.zeros((240, 240, 3), dtype=np.float32)
        
    def initializeGL(self) -> None:
        self.ctx = moderngl.create_context()
        
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 440
                
                in vec2 position;
                
                out vec2 v_texcoord;
                
                void main() {
                    gl_Position = vec4(position, 0.0, 1.0);
                    v_texcoord = position * 0.5 + 0.5;
                    v_texcoord.y = 1.0 - v_texcoord.y;
                }
            ''',
            fragment_shader='''
                #version 440
                
                uniform sampler2D image;
                uniform sampler2D box;
                
                in vec2 v_texcoord;
                
                out vec4 fragColor;
                
                void main() {
                    vec4 boxColor = texture(box, v_texcoord);
                    float data = texture(image, v_texcoord).r;
                    fragColor = vec4(vec3(data), 1.0) + boxColor * boxColor.a;
                }
            '''
        )
        
        self.histogramVBO = self.ctx.buffer(np.array([[-1, -1], [1, -1], [-1, 1], [1, 1]], dtype='f4'))
        self.histogramIBO = self.ctx.buffer(np.array([0, 1, 2, 2, 1, 3], dtype='i4'))
        self.histogramVAO = self.ctx.vertex_array(self.prog, [self.histogramVBO.bind('position')], self.histogramIBO)
        
        self.prog['image'] = 0
        self.prog['box'] = 1
        
        self.imageTex = self.ctx.texture((240, 240), 3, self.data.tobytes(), dtype='f4')
        self.boxTex = self.ctx.texture((240, 240), 4, self.box.tobytes(), dtype='f4')
    
    def paintGL(self) -> None:
        self.ctx.clear(0.5, 0.5, 0.5)
        
        
        self.imageTex.write(self.data.tobytes())
        self.boxTex.write(self.box.tobytes())
        
        self.imageTex.use(0)
        self.boxTex.use(1)
        self.histogramVAO.render(moderngl.TRIANGLES)
    
    def resizeGL(self, width: int, height: int) -> None:
        width = max(2, width)
        height = max(2, height)
        self.ctx.viewport = (0, 0, width, height)
    