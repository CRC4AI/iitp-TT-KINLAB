import sys
from PyQt5.QtGui import QPaintEvent, QPainter, QColor, QPen, QBrush, QPainterPath, QFont, QFontDatabase, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QTextEdit, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt
        
class InfoWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 1300, 1000)
        self.setWindowTitle('IITP-Turing Test')
        # white background
        self.setStyleSheet("background-color: white;")
        
        self.nameLabel = QLabel('성함\n(별칭도 괜찮습니다)', self)
        self.nameLabel.setStyleSheet("QLabel { background-color : #004191; font-size: 20px; font-weight: bold; color: white;}")
        self.jobLabel = QLabel('직종', self)
        self.jobLabel.setStyleSheet("QLabel { background-color : #004191; font-size: 20px; font-weight: bold; color: white;}")
        self.careerLabel = QLabel('경력(연차)', self)
        self.careerLabel.setStyleSheet("QLabel { background-color : #004191; font-size: 20px; font-weight: bold; color: white;}")
        
        self.nameText = QTextEdit(self)
        
        self.jobDropbox = QComboBox(self)
        self.jobDropbox.addItem('MD')
        self.jobDropbox.addItem('Non-MD')
        self.jobDropbox.addItem('Student')
        self.jobDropbox.addItem('Others')
        self.jobText = QTextEdit(self)
        
        # self.careerDropbox = QComboBox(self)
        # self.careerDropbox.addItem('1년 미만')
        # self.careerDropbox.addItem('5년 미만')
        # self.careerDropbox.addItem('5년 이상')
        # self.careerDropbox.addItem('기타')
        self.careerText = QTextEdit(self)
        
        self.nameLabel.setGeometry(280, 275, 180, 50)
        self.nameText.setGeometry(500, 275, 520, 50)
        self.jobLabel.setGeometry(280, 375, 180, 50)
        self.jobDropbox.setGeometry(500, 375, 150, 50)
        self.jobText.setGeometry(680, 375, 340, 50)
        self.careerLabel.setGeometry(280, 475, 180, 50)
        #self.careerDropbox.setGeometry(650, 675, 150, 50)
        self.careerText.setGeometry(500, 475, 520, 50)
        
        self.kaist_logo = QPixmap("./src/data/kaist_logo.png")
        self.cgv_logo = QPixmap("./src/data/cgv_logo.png")
        
        self.kaist_logo = self.kaist_logo.scaledToHeight(100)
        self.cgv_logo = self.cgv_logo.scaledToHeight(100)
        
        self.kaist_label = QLabel(self)
        self.kaist_label.setPixmap(self.kaist_logo)
        self.kaist_label.setGeometry(100, 800, 400, 100)
        
        self.cgv_label = QLabel(self)
        self.cgv_label.setPixmap(self.cgv_logo)
        self.cgv_label.setGeometry(1000, 800, 200, 100)
        
        self.nextButton = QPushButton("START", self)
        self.nextButton.setGeometry(550, 620, 200, 100)
        self.nextButton.clicked.connect(self.parent.goto_next_tab)
        self.nextButton.setStyleSheet("background-color: #004191; color: white; font-size: 30px; font-weight: bold; border-radius: 10px;")
        
        self.show()
        
    def paintEvent(self, a0: QPaintEvent) -> None:
        qp = QPainter()
        qp.begin(self)
        
        qp.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(250, 200, 800, 400, 40, 40)
        # p = QPen(QColor(0, 0, 0), 0)
        # qp.setPen(p)
        b = QBrush(QColor(0, 65, 145), Qt.SolidPattern)
        qp.setBrush(b)
        qp.fillPath(path, QColor(255, 255, 255))
        qp.drawPath(path)
        
        qp.end()
        
    def get_data(self):
        name = self.nameText.toPlainText()
        name = name.replace(" ", "_")
        name = name.replace("\n", "")
        name = name.replace("\t", "")
        job = self.jobDropbox.currentText()
        job_specific = self.jobText.toPlainText()
        career = self.careerText.toPlainText()
        return {"name":name,
                "job":job,
                "job_specific":job_specific,
                "career":career}