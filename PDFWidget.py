import sys,tempfile
from threading import Thread
from queue import Queue
from PyQt5.QtWidgets import (QWidget,QApplication,QListView,QListWidget,QLabel,
                                QVBoxLayout,QListWidgetItem,QFileDialog,QMessageBox
                             )
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtCore import QSize,Qt,pyqtSignal

from UI.UI_ReadPDF import Ui_widgetReadPDF

import fitz
import os
import win32api
import win32print

FactoryList = [2,1.8,1.6,1.4,1.2,1,0.8,0.6,0.4,0.2]
#QImage 辅助类
class PdfImage():
    def __init__(self,index,image):
        self.index = index
        self.image = image

    def getIndex(self):
        return self.index

    def getImage(self):
        return self.image

#主显示界面辅助类
class ShowImageWidget(QLabel):
    def __init__(self, *args, **kwargs):
        super(ShowImageWidget, self).__init__(*args, **kwargs)  # 继承父类
        self.setMouseTracking(True)  # 保证得到鼠标信息
        self.m_pixmap = None         # 原始QPixmap图像
        self.m_factor = 1            # 缩放因子

    # 设置显示图片
    def setpix(self, pix):
        self.m_pixmap = pix
        self.setPixmap(pix)

    # 鼠标滚轮事件
    def wheelEvent(self, ev):
        if ev.modifiers() & Qt.ControlModifier:  # 鼠标左键及Ctrl同时按下
            if ev.angleDelta().y() > 0:
                self.m_factor = self.m_factor * 1.05
            else:
                if self.m_factor > 0.2:
                    self.m_factor = self.m_factor * 0.95
            width = int(self.m_pixmap.width() * self.m_factor)
            height = int(self.m_pixmap.height() * self.m_factor)
            self.setPixmap(self.m_pixmap.scaled(QSize(width, height)))

    #按照缩放比例因子调整显示比例
    def setCustomScaled(self,factor):
        self.m_factor = factor
        width = int(self.m_pixmap.width() * self.m_factor)
        height = int(self.m_pixmap.height() * self.m_factor)
        self.setPixmap(self.m_pixmap.scaled(QSize(width, height)))

class WidgetPDF(QWidget,Ui_widgetReadPDF):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.bOpened = False  # 文档是否打开
        self.pdfName = "./111.pdf"  # 文档名
        self.nPages = 0  # 文档总页数
        self.nCurr = -1  # 当前文档页码
        self.docDoc = None  # 当前pymupdf文档对象
        #self.bModified = False  # 是否已编辑过
        #self.bShrink = False  # 列表框收缩标志
        self.nMaxPages = 32  # 最大显示页数
        self.IMAGE_SIZE = QSize(147, 208)  # A4纸210*297, 乘0.7
        self.LISTITEM_SIZE = QSize(160, 250)
        self.factory = 1    #缩放因子为1

        self.iniUi()


    # 初始化listWidget
    def iniUi(self):

        self.listWidget.setViewMode(QListWidget.IconMode)
        self.listWidget.setIconSize(self.IMAGE_SIZE)  # Icon 大小
        self.listWidget.setMovement(QListView.Static)  # Listview显示状态
        self.listWidget.setResizeMode(QListView.Adjust)
        self.listWidget.setSpacing(12)  # 间距大小
        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #self.showMaximized()

    # 设置窗口菜单控件状态
    def set_window_status(self):
        pass

    # 初始化事件
    def init_event_plot(self):
        #缩略图单击事件
        self.listWidget.clicked.connect(self.onclicked_listWidget)
        # 另存为
        self.btn_Download.released.connect(self.onclicked_actionSaveAs)
        # 打印pdf文档
        self.btn_Print.released.connect(self.onclicked_actionPrint)
        #上一页
        self.btn_PageUp.released.connect(self.onclicked_pageUp)
        #下一页
        self.btn_PageDown.released.connect(self.onclicked_pageDown)
        #跳转指定页
        self.lineEdit_CurrentPage.returnPressed.connect(self.enter_toPage)
        #设定放大比例
        self.comboBox_factor.currentIndexChanged.connect(self.onclicked_select_factory)
        #减少放大比例
        self.btn_ZoomSamller.released.connect(self.onclicked_zoom_samller)
        #增加放大比例
        self.btn_ZoomLarger.released.connect(self.onclicked_zoom_larger)


    # 打开文档处理
    def open_doc(self):
        if self.pdfName:
            #row = self.cur.execute("SELECT FileBinary From BookFile where ID = ?;", (3,))
            #self.pdfName = row.fetchone()[0]
            #self.docDoc = fitz.open(None,row.fetchone()[0],'pdf')
            self.docDoc = fitz.open(self.pdfName)
            self.bOpened = True  # 设置文件打开
            #self.labelFileName.setText(self.pdfName)
            self.refresh_listWidget()
            # 显示第一页
            self.nCurr = 0
            self.show_current_page()


# 刷新listWidget

    #加载左侧缩略图
    def refresh_listWidget(self):
        if not self.bOpened:
            return
        self.set_window_status()    # 刷新菜单状态
        self.listWidget.clear()
        self.nPages = self.docDoc.pageCount
        self.label_pages.setText("/"+str(self.nPages))
        if self.nPages <= 0:
            return
        for i in range(0, self.nPages):
            page = self.docDoc[i]  # 当前页
            zoom = int(30)
            rotate = int(0)
            trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).preRotate(rotate)
            pix = page.getPixmap(matrix=trans, alpha=False)
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            qtimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)  # 当前页转换为QImage对象

            widget = QWidget(self)
            vboxLayout = QVBoxLayout()
            widget.setLayout(vboxLayout)
            listItem = QListWidgetItem(self.listWidget)  # 列表控件项
            listItem.setSizeHint(self.LISTITEM_SIZE)
            labelimg = QLabel(widget)
            labelimg.setPixmap(QPixmap.fromImage(qtimg).scaled(self.IMAGE_SIZE))  # 显示在一个QLabel上
            labelimg.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            labeltxt = QLabel(widget)  # 页码序号
            labeltxt.setText("%d" % int(i + 1))
            labeltxt.setFixedHeight(30)
            labeltxt.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            labeltxt.setWordWrap(True)
            vboxLayout.addWidget(labelimg)  # 图片和页码加入vboxLayout
            vboxLayout.addWidget(labeltxt)
            widget.setFixedHeight(self.LISTITEM_SIZE.height())

            self.listWidget.setItemWidget(listItem, widget)  # 显示到listWidget中
        listItem = QListWidgetItem(self.listWidget)  # listWidget最后一项显示异常,因此多加一项,需要再排查优化
        listItem.setSizeHint(QSize(0, 0))

    # 显示当前页
    def show_current_page(self):
        if not self.bOpened or self.nPages <= 0:
            return
        if self.nCurr < 0:
            return
        if self.nCurr >= self.nPages:
            self.nCurr = self.nPages - 1

        # 得到当前页
        page = self.docDoc[self.nCurr]
        zoom = int(200)
        rotate = int(0)
        trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).preRotate(rotate)
        pix = page.getPixmap(matrix=trans, alpha=False)
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        qtimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt) # 当前页转换为QImage对象
        # 准备显示控件
        widget = QWidget(self)
        vboxLayout = QVBoxLayout()
        labelimg = ShowImageWidget(widget)  # 使用一个自定义的QLabel控件
        labelimg.setpix(QPixmap.fromImage(qtimg).scaled(QSize(pix.width, pix.height)))
        labelimg.setCustomScaled(self.factory)
        labelimg.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        vboxLayout.addWidget(labelimg)
        widget.setLayout(vboxLayout)
        self.showArea.setWidget(widget)    # 添加到showArea

        # 更新状态栏页码和顶部操作栏的页面
        self.label_FileStatus.setText("第 %d 页/共 %d 页" % (int(self.nCurr + 1), self.nPages))
        self.lineEdit_CurrentPage.setText(str(self.nCurr + 1))

    # 缩略图列表控件单击事件
    def onclicked_listWidget(self, index):
        self.nCurr = index.row()
        self.show_current_page()

    # 另存为
    def onclicked_actionSaveAs(self):
        if not self.bOpened:
            return
        filePath, fname = os.path.split(os.path.abspath(self.pdfName))
        newfileName, ok = QFileDialog.getSaveFileName(self, "文件另存为", filePath, "*.pdf")
        if newfileName:
            self.docDoc.save(newfileName)
            #先关闭当前文档
            self.bOpened = False  # 文档是否打开
            self.bModified = False
            self.pdfName = None  # 文档名
            self.nPages = 0  # 文档总页数
            self.nCurr = -1  # 当前文档页码
            self.docDoc = None  # 当前pymupdf文档对象
            #再打开新文档
            self.pdfName = newfileName
            self.labelFileName.setText(self.pdfName)
            self.docDoc = fitz.open(self.pdfName)
            self.bOpened = True  # 设置文件打开
            self.refresh_listWidget()
            # 显示第一页
            self.nCurr = 0
            self.show_current_page()

# 打印pdf文档

    #打印
    def onclicked_actionPrint(self):
        #if not self.bOpened :
        #    return
        #if self.bModified:
        #    QMessageBox.information(self, "Information", "已修改，请先保存", QMessageBox.Ok)
        #    return

        win32api.ShellExecute(
            0,
            "print",
            self.pdfName,
            #
            # If this is None, the default printer will
            # be used anyway.
            #
            '/d:"%s"' % win32print.GetDefaultPrinter(),
            ".",
            0
        )

    #单击上一页
    def onclicked_pageUp(self):
        inputPage = self.lineEdit_CurrentPage.text()
        if inputPage.isnumeric() == False:
            return
        currentPage = int(inputPage) - 1
        upPage = currentPage - 1
        if upPage < 0:
            return
        else:
            self.nCurr = upPage
            self.show_current_page()

    #下一页
    def onclicked_pageDown(self):
        inputPage = self.lineEdit_CurrentPage.text()
        if inputPage.isnumeric() == False:
            return
        currentPage = int(inputPage) - 1

        nextPage = currentPage + 1
        if nextPage > self.nPages:
            return
        else:
            self.nCurr = nextPage
            self.show_current_page()

    #Enter跳转到指定页面
    def enter_toPage(self):
        inputPage = self.lineEdit_CurrentPage.text()
        if inputPage.isnumeric() == False:
            return
        currentPage = int(inputPage) - 1
        if currentPage < 0 or currentPage > self.nPages:
            return
        else:
            self.nCurr = currentPage
            self.show_current_page()
    #选择放大因子，并重新显示
    def onclicked_select_factory(self):
        index = self.comboBox_factor.currentIndex()
        self.factory = FactoryList[index]
        self.show_current_page()

    #槽，响应缩小因子
    def onclicked_zoom_samller(self):
        index = self.comboBox_factor.currentIndex()
        if index == 9:
            return
        else:
            index = index + 1
            self.comboBox_factor.setCurrentIndex(index)
    #槽，响应放大因子
    def onclicked_zoom_larger(self):
        index = self.comboBox_factor.currentIndex()
        if index == 0:
            return
        else:
            index = index - 1
            self.comboBox_factor.setCurrentIndex(index)

class WidgetPDFStream(WidgetPDF):
    signal_SaveOver = pyqtSignal(str)
    signal_OpenDoc = pyqtSignal()
    signal_HaveImage = pyqtSignal()

    def __init__(self,stream,title):
        super().__init__()
        #print(type(stream))
        self.stream = bytes(stream)
        self.docTitle = title
        self.imageQueue = Queue()
        self.init_event_plot()

        self.signal_SaveOver.connect(self.onSignalSaveOver)
        self.signal_OpenDoc.connect(self.onSignalOpenDocInitUI)
        self.signal_HaveImage.connect(self.onSignalHaveImageDisplayTree)

        self.openPdfByStreamThread()
        #self.open_docByStream()
    #以线程方式代开文档
    def openPdfByStreamThread(self):
        try:
            def func():
                self.docDoc = fitz.open(None, self.stream, 'PDF')
                self.bOpened = True
                #成功打开后发射
                self.signal_OpenDoc.emit()
            openThread = Thread(target=func)
            openThread.start()
        except:
            pass

    #以线程方式加载左侧树，并生成QImage队列
    def onSignalOpenDocInitUI(self):
        self.nPages = self.docDoc.pageCount#总页数
        self.label_pages.setText("/" + str(self.nPages))
        self.label_FileStatus.setText("载入中，请稍后...")
        self.listWidget.clear()  # 刷新左侧树
        def func1():
            zoom = int(30)
            rotate = int(0)
            trans = fitz.Matrix(zoom / 100.0, zoom / 100.0).preRotate(rotate)

            for i in range(0,self.nPages):
                page = self.docDoc[i]  # 当前页
                pix = page.getPixmap(matrix=trans, alpha=False)
                fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
                qtimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
                self.imageQueue.put(PdfImage(i,qtimg))
            self.signal_HaveImage.emit()

        imageThread = Thread(target=func1)
        imageThread.start()

    def onSignalHaveImageDisplayTree(self):
        while self.imageQueue.qsize() != 0:
            pdfImage = self.imageQueue.get()
            qtimg = pdfImage.getImage()
            current = pdfImage.getIndex()

            widget = QWidget(self)
            vboxLayout = QVBoxLayout()
            widget.setLayout(vboxLayout)
            listItem = QListWidgetItem(self.listWidget)  # 列表控件项
            listItem.setSizeHint(self.LISTITEM_SIZE)
            labelimg = QLabel(widget)
            labelimg.setPixmap(QPixmap.fromImage(qtimg).scaled(self.IMAGE_SIZE))  # 显示在一个QLabel上
            labelimg.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            labeltxt = QLabel(widget)  # 页码序号
            labeltxt.setText("%d" % int(current + 1))
            labeltxt.setFixedHeight(30)
            labeltxt.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            labeltxt.setWordWrap(True)
            vboxLayout.addWidget(labelimg)  # 图片和页码加入vboxLayout
            vboxLayout.addWidget(labeltxt)
            self.listWidget.addItem(listItem)
            widget.setFixedHeight(self.LISTITEM_SIZE.height())
            self.listWidget.setItemWidget(listItem, widget)  # 显示到listWidget中

        self.nCurr = 0
        self.show_current_page()

    def open_docByStream(self):
        try:
            #row = self.cur.execute("SELECT FileBinary From BookFile where ID = ?;", (3,))
            #self.pdfName = row.fetchone()[0]
            #print("OPen PDF:::")
            #print(type(self.stream))
            self.docDoc = fitz.open(None,self.stream,'PDF')
                #self.docDoc = fitz.open(self.pdfName)
            #print(self.docDoc)
            self.bOpened = True  # 设置文件打开
                #self.labelFileName.setText(self.pdfName)
            self.refresh_listWidget()
                # 显示第一页
            self.nCurr = 0
            self.show_current_page()
        except:
            pass
    #打印
    def onclicked_actionPrint(self):
        if self.bOpened == True:
            newFileName = tempfile.mktemp(".pdf")
            self.docDoc.save(newFileName)
            print("stream print")
            win32api.ShellExecute(
                0,
                "print",
                newFileName,
                '"%s"' % win32print.GetDefaultPrinter(),
                ".",
                0
            )

   # 另存为

    def onclicked_actionSaveAs(self):

        newfileName, ok = QFileDialog.getSaveFileName(self, "文件另存为", os.getcwd()+"\\"+self.docTitle+".pdf", "*.pdf")
        if ok:
            #self.docDoc.save(newfileName)
            def func():
                self.docDoc.save(newfileName)
                self.signal_SaveOver.emit(newfileName)
            saveThread = Thread(target=func)
            saveThread.start()

        else:
            return

    #槽函数，提示另存成功
    def onSignalSaveOver(self,name):
        QMessageBox.information(self, "提示", name + "文件另存为成功！")


if __name__ == '__main__':
    mainAPP = QApplication(sys.argv)
    mainWin = WidgetPDF()
    #mainWin = WidgetPDFStream(1,2,3)
    mainWin.show()

    sys.exit(mainAPP.exec_())