import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QWidget, QTabWidget
from PyQt5.QtGui import QMouseEvent, QFont, QFontDatabase
from PyQt5 import uic, QtCore, QtOpenGL
from PIL import Image
import json

import moderngl
import numpy as np

import random

from src import TesterWidget
from src import AnswerWidget
from src import InfoWidget

form_class = uic.loadUiType("main.ui")[0]

DATA_LENGTH = 15
SYNTH_DATA_LENGTH = 9
REAL_DATA_LENGTH = 6

class MyAppWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.data_length = DATA_LENGTH
        
        self.data = []
        self.data_list = [] 
        
        seed = random.choice([0,1])

        if seed == 0:
            real_dir = 'real_sh/'
            synth_dir = 'synth_sh/'
        else:
            real_dir = 'real_jh/'
            synth_dir = 'synth_jh/'

        print('suhyun' if seed == 0 else 'jihoon')

        self.real_data_list = os.listdir('./data/' + real_dir)
        self.real_data_list = [real_dir + f for f in self.real_data_list]
        self.synth_data_list = os.listdir('./data/' + synth_dir)
        self.synth_data_list = [synth_dir + f for f in self.synth_data_list]
        
        self.randomize_data()
        
        self.initUI()
        
        
    def initUI(self):
        self.info_tab = InfoWidget(self)
        self.test_tab = TesterWidget(self)
        self.answer_tab = AnswerWidget(self)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.info_tab, 'Info')
        self.tabs.addTab(self.test_tab, 'Test')
        
        
        self.setCentralWidget(self.tabs)
        
        self.show()
        
        self.tabs.currentChanged.connect(self.tab_changed)
        
    def save_data(self):
        info_data = self.tabs.widget(0).get_data()
        data = {"info":info_data, "score":self.answer_tab.score_calculate(), "data":self.data_list, "test":self.test_tab.get_data(), "bounding_box":self.answer_tab.get_data()}
        name = info_data["name"]
        with open("./save/" + name + ".json", 'w', encoding="UTF-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
                
    def tab_changed(self, index):
        if index == 1:
            self.save_data()
            self.test_tab.timer_start()
        elif index == 2:
            self.answer_tab.get_answer()
            self.answer_tab.reset_text()
            
    def randomize_data(self):
        if (self.data_length != (SYNTH_DATA_LENGTH + REAL_DATA_LENGTH)):
            assert False, "Data length should be same as the sum of synth and real data length"
        real_data_list = random.sample(self.real_data_list, REAL_DATA_LENGTH)
        synth_data_list = random.sample(self.synth_data_list, SYNTH_DATA_LENGTH)
        self.data_list = random.sample(real_data_list + synth_data_list, self.data_length)
        for f in self.data_list:
            self.data.append(np.array(Image.open('./data/' + f), dtype=np.float32) / 255.0)
            
    def answer_tab_add(self):
        self.tabs.addTab(self.answer_tab, 'Answer')
        
    def goto_next_tab(self):
        self.tabs.setCurrentIndex(self.tabs.currentIndex() + 1)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    fontDB = QFontDatabase()
    fontDB.addApplicationFont('malgun.ttf')
    app.setFont(QFont('맑은 고딕', 12))
    
    myWindow = MyAppWindow()
    sys.exit(app.exec_())
    