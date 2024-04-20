import os
import sqlite3
import hashlib
from threading import Thread
from PyQt5.QtWidgets import QWidget,QAbstractItemView,QMessageBox,QDataWidgetMapper,QFileDialog
from PyQt5.QtSql import QSqlQuery,QSqlQueryModel
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtGui import QIcon

from MinTaiSongZaiDB import MainWindow
from CreateDB import SingleDBConnect
from PDFWidget import WidgetPDFStream

from UI.Ui_AdminAddItemWidget import Ui_AddItemWidget

class AdminAddItemWidget(QWidget):
    def __init__(self,mainWin=MainWindow):
        super().__init__()
        self.ui = Ui_AddItemWidget()
        self.ui.setupUi(self)
        self.mainWin = mainWin

        self.conn = sqlite3.connect("./DB/MTSongZaiDB.db")
        self.cur = self.conn.cursor()

        #信号绑定
        #清空信息页面内容
        self.ui.pbnCancer.clicked.connect(self.on_clear)

        #信号槽绑定
        #提交按钮
        self.ui.pbnSubmit.clicked.connect(self.on_submit)

        #信号槽绑定
        #获取上传PDF路劲
        self.ui.pbnLoadPDF.clicked.connect(self.on_loadPDFUrl)

        #信号绑定
        #一级目录选择改变
        self.ui.comBoxClass1.activated.connect(self.on_class1Change)

        #信号绑定
        #二级目录选择改变
        self.ui.comBoxClass2.activated.connect(self.on_class2Change)

        #初始化一二三级目录
        self.on_class1Change()

    #槽，响应一级目录选择改变
    def on_class1Change(self):
        class1 = self.ui.comBoxClass1.currentText()
        if class1 == "褒歌":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass2.addItems(["百样花歌", "落阴", "清心", "青暝缚脚", "火车相褒", "撞球", "茶园", "其他"])
            self.ui.comBoxClass2.setCurrentIndex(0)
            self.ui.comBoxClass3.clear()
        elif class1 == "传统故事":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass2.addItems(["山伯英台", "陈三五娘", "刘廷英", "孟姜女", "斩太子", "孟丽君", "案件", "零散的","三勇士",\
                                           "孙悟空","哪吒","白蛇故事","王昭君","玉堂春","玉环记","才子歌","橄榄记","大禹","卖油郎花魁女",\
                                           "最新玉杯记歌","包公","三国","月台梦","郑元和","朱买臣"])
            self.ui.comBoxClass2.setCurrentIndex(0)
            self.ui.comBoxClass3.clear()
            self.on_class2Change()
        elif class1 == "民间歌谣与民间传说故事":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass2.addItems(["死某歌", "侥幸歌", "手巾歌", "雪梅思君", "陈白笔", "金姑看羊", "番婆弄", "梁士奇","桃花女",\
                                           "探娘探嫂探哥","十二碗菜","白贼七","其他"])
            self.ui.comBoxClass2.setCurrentIndex(0)
            self.ui.comBoxClass3.clear()
        elif class1 == "劝世教化":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass2.addItems(["文明维新", "地震水灾", "商络", "婚姻恋爱", "劝世", "鸦片", "人心", "游戏逍遥酒色花花世界","摇古歌",\
                                           "人之初","其他"])
            self.ui.comBoxClass2.setCurrentIndex(0)
            self.ui.comBoxClass3.clear()
        elif class1 == "生活知识":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass2.addItems(["四民经济", "其他"])
            self.ui.comBoxClass2.setCurrentIndex(0)
            self.ui.comBoxClass3.clear()
        elif class1 == "习俗趣味":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass2.addItems(["蚊子", "三婿祝寿","乌猫"])
            self.ui.comBoxClass2.setCurrentIndex(0)
            self.ui.comBoxClass3.clear()
        elif class1 == "叙情":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass2.addItems(["臭头娘子", "白扇记","其他"])
            self.ui.comBoxClass2.setCurrentIndex(0)
            self.ui.comBoxClass3.clear()
        elif class1 == "其他":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass2.addItems(["地理歌", "日本话","电影荒江女侠","其他"])
            self.ui.comBoxClass2.setCurrentIndex(0)
            self.ui.comBoxClass3.clear()
        elif class1 == "时事新编":
            self.ui.comBoxClass2.clear()
            self.ui.comBoxClass3.clear()

    #槽，响应二级目录选择改变
    def on_class2Change(self):
        class1 = self.ui.comBoxClass1.currentText()
        class2 = self.ui.comBoxClass2.currentText()
        if class2 == "山伯英台":
            self.ui.comBoxClass3.clear()
            self.ui.comBoxClass3.addItems(["出世", "归天", "留学", "马家","三伯出山","三伯回阳回魂","三伯探英台",\
                                           "游地府","游西湖","纸歌","其他"])
            self.ui.comBoxClass3.setCurrentIndex(0)
        else:
            self.ui.comBoxClass3.clear()


    #槽，响应获取PDFURL
    def on_loadPDFUrl(self):
        try:
            fname,_=QFileDialog.getOpenFileName(self,"打开PDF文件",".","PDF文件(*.pdf)")
            self.ui.labelPath.setText(fname)
        except:
            pass

    #槽，响应重置按钮
    def on_clear(self):
        self.ui.comBoxClass1.setCurrentIndex(0)
        self.on_class1Change()
        self.on_class2Change()
        self.ui.lineEditBookName.clear()
        self.ui.lineEditPerson.clear()
        self.ui.lineEditPages.clear()
        self.ui.lineEditEditStyle.clear()
        self.ui.lineEditPublish.clear()
        self.ui.lineEditAuthor.clear()
        self.ui.lineEditYear.clear()
        self.ui.lineEditAge.clear()
        self.ui.lineEditTitle.clear()
        self.ui.labelPath.clear()
        self.ui.textEditSummary.clear()


    #槽，响应按钮添加动作
    def on_submit(self):
        bookName = self.ui.lineEditBookName.text().strip()
        url = self.ui.labelPath.text().strip()
        print(bookName)
        if bookName =="":
            QMessageBox.warning(self,"警告","篇名内容不能为空！",QMessageBox.Ok,QMessageBox.Ok)
        elif url == "":
            QMessageBox.warning(self, "警告", "请上传PDF文档！", QMessageBox.Ok, QMessageBox.Ok)
        else:
            class1 = self.ui.comBoxClass1.currentText()
            class2 = self.ui.comBoxClass2.currentText()
            class3 = self.ui.comBoxClass3.currentText()
            if class2 == "":
                class2 = None
            if class3 == "":
                class3 = None
            title = self.ui.lineEditTitle.text().strip()
            if title == "":
                title = None
            age = self.ui.lineEditAge.text().strip()
            if age == "":
                age = None
            year = self.ui.lineEditYear.text().strip()
            if year == "":
                year = None
            author = self.ui.lineEditAuthor.text().strip()
            if year == "":
                year = None
            publish = self.ui.lineEditPublish.text().strip()
            if publish == "":
                publish = None
            editStyle = self.ui.lineEditEditStyle.text().strip()
            if editStyle == "":
                editStyle = None
            pages = self.ui.lineEditPages.text().strip()
            if pages == "":
                pages = None
            person = self.ui.lineEditPerson.text().strip()
            if person == "":
                person = None
            summary = self.ui.textEditSummary.toPlainText()
            if summary =="":
                summary = None
            #执行添加操作
            try:
                pdfBinary = None
                pdfFile = open(url, "rb")
                pdfBinary = pdfFile.read()
                hash_md5 = (hashlib.md5(pdfBinary).hexdigest())
                pdfFile.close()
                self.cur.execute("INSERT  INTO Song VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", \
                (None, bookName, title, year, age, author, publish, editStyle, summary, person, pages, class1, class2, class3, hash_md5,url))
                self.conn.commit()
                self.cur.execute("INSERT  INTO SongFile VALUES(?,?,?)",(None,hash_md5,pdfBinary))
                self.conn.commit()
            except IOError:
                print("文件问题")
            QMessageBox.information(self,"提示",bookName + "\n添加完成！",QMessageBox.Yes,QMessageBox.Yes)
            self.on_clear()
