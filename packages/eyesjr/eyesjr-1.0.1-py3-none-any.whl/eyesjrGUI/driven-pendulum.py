#from __future__ import print_function
import os, sys, time, inspect, os.path
from . import utils

from .QtVersion import *

class ListStream:
    def __init__(self):
            self.data = ''
    def write(self, s):
            self.data += s


class Expt(QWidget):
	functionList = {}
	mycode = ''
	TIMER = 500
	
	def __init__(self, device=None):
		QWidget.__init__(self)
		self.p = device										# connection to the device hardware 		


		full = QVBoxLayout()
		
		self.Edit = QTextEdit()	
		full.addWidget(self.Edit)
		font = QFont()
		font.setPointSize(16)
		self.Edit.setFont(font)

		s=self.tr('SQ1 Frequency can be changed from 1 Hz to 50Hz')
		self.Edit.setText(s)	
	
		H = QHBoxLayout()
		l = QLabel(text=self.tr('Set SQ1'))
		l.setMaximumWidth(60)
		H.addWidget(l)

		self.SQ1slider = utils.slider(100, 5000, 100, 1000,self.sq1_slider)
		H.addWidget(self.SQ1slider)
		full.addLayout(H)

		self.msgwin = QLabel(text='')
		self.msgwin.setStyleSheet('background-color: white')
		full.addWidget(self.msgwin)
				
		self.setLayout(full)	
		self.timer = QTimer()

		#----------------------------- end of init ---------------

	def sq1_slider(self, val):
		try:
			res = self.p.set_sqr1(val*0.01)
			ss = '%5.2f'%res
			self.msg(self.tr('sqr1 set to ') + ss + self.tr(' Hz'))
		except:
			self.comerr()
					
	def msg(self, m):
		self.msgwin.setText(self.tr(m))
		
	def comerr(self):
		self.msgwin.setText('<font color="red">' + self.tr('Error. Try Device->Reconnect'))

if __name__ == '__main__':
	import eyesjun.eyes
	dev = eyesjun.eyes.open()
	app = QApplication(sys.argv)

	# translation stuff
	lang=QLocale.system().name()
	t=QTranslator()
	t.load("lang/"+lang, os.path.dirname(__file__))
	app.installTranslator(t)
	t1=QTranslator()
	t1.load("qt_"+lang,
	        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
	app.installTranslator(t1)

	mw = Expt(dev)
	mw.show()
	sys.exit(app.exec_())
	
