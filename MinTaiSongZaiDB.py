import sys
from PyQt5.QtWidgets import QApplication,QMainWindow,QTabWidget
from UI.UI_SongZaiMainWin import Ui_MainWindow


from SongListWidget import SongListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 设置标签主显示页
        self.cenTab = QTabWidget()
        self.cenTab.setTabsClosable(True)
        self.cenTab.tabCloseRequested.connect(self.on_cenTab_close)
        self.setCentralWidget(self.cenTab)

        #设置信号槽
        self.ui.actionHome.triggered.connect(self.on_open_songZaiTab)
        self.ui.actionQuit.triggered.connect(self.close)

        #初始化歌仔册页面对象
        self.songIndexTab = SongListWidget()

        self.on_open_songZaiTab()




    #槽，关闭标签页
    def on_cenTab_close(self,index):
        self.cenTab.removeTab(index)

    #激活歌仔册资料库页
    def on_open_songZaiTab(self):
        self.cenTab.addTab(self.songIndexTab, "歌仔册数据库")
        self.cenTab.setCurrentWidget(self.songIndexTab)



if __name__ == "__main__":
    mainApp = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.showMaximized()
    sys.exit(mainApp.exec_())