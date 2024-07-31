import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QWidget
from PyQt5.QtGui import QMouseEvent
from PyQt5 import uic, QtCore, QtOpenGL
from PIL import Image
import json

import moderngl
import numpy as np

import time
import datetime

WAIT_TIME = 0.1

form_class = uic.loadUiType("./src/UI/tester.ui")[0]

class TesterWidget(QWidget, form_class):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        
        self.parent = parent
        
        self.init_ui()
        
        self.data_length = self.parent.data_length
        self.answer = [[-1, 0] for _ in range(self.data_length)]
        self.box = {}
        
        self.data = self.parent.data
                    
        self.renderWindow.data = self.data[0]
        
        self.index: int = 0
        
        self.indexDisplay.append("image 1/" + str(self.data_length))
        self.answerDisplay.setText("Your Answer: ")
        
    
    def init_ui(self):
        self.realButton.clicked.connect(self.select_real)
        self.synthButton.clicked.connect(self.select_synth)
        self.nextButton.clicked.connect(self.next)
        #self.saveButton.clicked.connect(self.save_data)
        #self.loadButton.clicked.connect(self.load_data)
        
        self.indexDisplay.setStyleSheet("font-size: 30px; font-weight: bold; border: 0;")
        self.answerDisplay.setStyleSheet("font-size: 30px; border: 0;")
        
        self.realButton.setStyleSheet("background-color: green; color: white; font-size: 30px; font-weight: bold; border-radius: 10px;")
        self.synthButton.setStyleSheet("background-color: red; color: white; font-size: 30px; font-weight: bold; border-radius: 10px;")
        self.nextButton.setStyleSheet("background-color: #004191; color: white; font-size: 30px; font-weight: bold; border-radius: 10px;")
        
        self.renderWindow = RenderWidget(self)
        self.renderWindow.setGeometry(30, 120, 720, 720)
        
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.renderWindow.updateGL)
        self.timer.start()
        
        self.show()
        
        self.test_finished = False
    
    def select_real(self):
        self.answer[self.index][0] = 1
        self.answerDisplay.setText("Your Answer:\nREAL")
    
    def select_synth(self):
        self.answer[self.index][0] = 0
        self.answerDisplay.setText("Your Answer:\nSYNTHETIC")
    
    def prev(self):
        if (self.index == 0):
            return
        self.index -= 1
        self.renderWindow.data = self.data[self.index]
        self.answer[self.index][1] = self.timer_check()
        self.indexDisplay.setText("image " + str(self.index + 1) + "/" + str(self.data_length))
    
    def next(self):
        if (self.test_finished):
            self.parent.goto_next_tab()
            return
        if (self.index == self.data_length - 1):
            self.answer[self.index][1] = self.timer_check()
            self.parent.save_data()
            # self.renderWindow.destroy()
            # self.indexDisplay.destroy()
            # self.realButton.destroy()
            # self.synthButton.destroy()
            # self.nextButton.destroy()
            self.answerDisplay.setText("Test Finished!")
            self.parent.answer_tab_add()
            self.realButton.clicked.disconnect()
            self.synthButton.clicked.disconnect()
            self.test_finished = True
            return
        if (time.time() - self.time < WAIT_TIME):
            return
        if (self.answer[self.index][0] == -1):
            return
        self.answer[self.index][1] = self.timer_check()
        self.index += 1
        self.renderWindow.data = self.data[self.index]
        self.indexDisplay.setText("image " + str(self.index + 1) + "/" + str(self.data_length))
        self.answerDisplay.setText("Your Answer: ")
        self.parent.save_data()
        
    def get_data(self):
        return self.answer
    
    def timer_start(self):
        self.time = time.time()
        
    def timer_check(self):
        end_time = time.time()
        delta_time = end_time - self.time
        self.time = end_time
        return delta_time
    
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
    