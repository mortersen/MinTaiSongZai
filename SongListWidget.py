from PyQt5.QtWidgets import QWidget,QAbstractItemView,QMessageBox,QDataWidgetMapper
from PyQt5.QtSql import QSqlQuery,QSqlQueryModel
from PyQt5.QtCore import Qt

from CreateDB import SingleDBConnect

from UI.UI_SongListWidget import Ui_SongListWidget


class SongListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SongListWidget()
        self.ui.setupUi(self)

        #初始化数据库对应表显示

        #用于查询
        self.DB = SingleDBConnect().DB
        self.DB.open()
        self.sqlQuery = QSqlQuery(self.DB)

        #用于同步表格,及控件
        self.qryModel = QSqlQueryModel(self)
        self.ui.tableView.setModel(self.qryModel)
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.qryModel)

        self.currentPage = 0
        self.eachPage = 40
        self.totalRecord = self.CaculateTotalRecord()
        self.ui.labelTotalRecord.setText("总"+str(self.totalRecord)+"条记录")
        self.pages = self.CaculatePages()
        self.ui.labelPages.setText(str(self.pages))

        self.SetCurrentPage()
        self.query = "SELECT BookName,Age,Author,Publish,EditStyle,MD5 FROM Song"
        self.condition = ""
        self.executeQurey(self.currentPage*self.eachPage)
        self.initTable()

        #设置信号
        #前一页
        self.ui.pbnUppage.clicked.connect(self.UpPage_Callback)
        #h后一页
        self.ui.pbnDownpage.clicked.connect(self.DoPage_Callback)

        #跳转页面
        self.ui.pbnGotoPage.clicked.connect(self.GotoPage_Callback)
        self.ui.lineEditGotoPage.returnPressed.connect(self.GotoPage_Callback)

        #槽，响应改变表格选择行事件
        self.selectionModel = self.ui.tableView.selectionModel()
        self.selectionModel.currentRowChanged.connect(self.do_currentRowChanged)

        #双击表格阅读歌册文档PDF
        self.ui.tableView.doubleClicked.connect(self.do_readSongZaiPDF)

        #单击阅读按钮阅读歌册文档PDF
        #self.ui.ptnRead.clicked.connect(self.do_read)

        #槽，按关键字搜索
        self.ui.pbnSearch.clicked.connect(self.do_searchKeyworld)
        self.ui.lineEditKeyWorld.returnPressed.connect(self.do_searchKeyworld)


        #信号,重新载入数据库
        self.ui.pbnReload.clicked.connect(self.do_reloadDB)

    # 初始化表格
    def initTable(self):
        self.ui.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.tableView.setSelectionModel(QAbstractItemView.SingleSelection)
        self.ui.tableView.setAlternatingRowColors(True)
        # 设置默认行高
        self.ui.tableView.verticalHeader().setDefaultSectionSize(60)
        #设置默认宽度
        self.ui.tableView.setColumnWidth(0, 500)
        self.ui.tableView.setColumnWidth(1, 220)
        self.ui.tableView.setColumnWidth(2, 220)
        #最后一列隐藏
        self.ui.tableView.setColumnHidden(5, True)

        self.qryModel.setHeaderData(0, Qt.Horizontal, "册名")
        self.qryModel.setHeaderData(1, Qt.Horizontal, "年代")
        self.qryModel.setHeaderData(2, Qt.Horizontal, "作者")
        self.qryModel.setHeaderData(3, Qt.Horizontal, "出版社")
        self.qryModel.setHeaderData(4, Qt.Horizontal, "版样")

        self.mapper.addMapping(self.ui.textEditBookName,0)
        self.mapper.addMapping(self.ui.lineEditAge,1)
        self.mapper.addMapping(self.ui.lineEditAuthor,2)
        self.mapper.addMapping(self.ui.lineEditPublish,3)
        self.mapper.addMapping(self.ui.lineEditEditStyle,4)

        self.mapper.toFirst()


    #计算总记录数
    def CaculateTotalRecord(self):
        try:
            self.sqlQuery.exec('SELECT 1 from Song')
            self.sqlQuery.last()
            return self.sqlQuery.at() + 1
        except Exception:
            print(Exception.__str__())

    #计算总页数
    def CaculatePages(self):
        #每页40条记录
        page = self.totalRecord // self.eachPage
        if self.totalRecord % self.eachPage != 0:
            page += 1
        return page

    #更新当前页数
    def SetCurrentPage(self):
        self.ui.labelCurrentPage.setText(str(self.currentPage + 1))

    #执行查询page
    def executeQurey(self, index):
        limit = " limit %d,%d" % (index, self.eachPage)
        query = self.query + self.condition + limit
        self.qryModel.setQuery(query)

    #槽，上一页
    def UpPage_Callback(self):
        if self.currentPage == 0:
            return
        self.currentPage = self.currentPage - 1
        self.executeQurey(self.currentPage * self.eachPage)
        self.SetCurrentPage()

    #槽，下一页
    def DoPage_Callback(self):
        if self.currentPage + 1== self.pages:
            return
        self.currentPage = self.currentPage + 1
        self.executeQurey(self.currentPage * self.eachPage)
        self.SetCurrentPage()

    #槽，跳转页面
    def GotoPage_Callback(self):
        target = self.ui.lineEditGotoPage.text().strip()
        if target.isnumeric() is False:
            QMessageBox.warning(self, "警告", "请输入正确的页码数字!", QMessageBox.Yes)
            self.ui.lineEditGotoPage.setText("")
            return
        targetPage = int(target)
        if targetPage < 1 or targetPage > self.pages:
            QMessageBox.warning(self, "警告", "请输入正确的页码数字!", QMessageBox.Yes)
            self.ui.lineEditGotoPage.setText("")
        else:
            self.currentPage = targetPage - 1
            self.executeQurey(self.currentPage * self.eachPage)
            self.SetCurrentPage()

    #槽，响应表格行选择改变
    def do_currentRowChanged(self,current,previous):
        self.mapper.setCurrentIndex(current.row())

    #槽，响应双击阅读歌册
    def do_readSongZaiPDF(self,index):
        curRec = self.qryModel.record(index.row())
        print(curRec.value("BookName"))
        #根据MD5查询是否有电子PDF，有仔标签页打开。


    #槽，响应关键字搜索
    def do_searchKeyworld(self):
        keyworld = self.ui.lineEditKeyWorld.text().strip()

        if len(keyworld) == 0:
            QMessageBox.information(self, "提示", "请输入搜索关键字!", QMessageBox.Yes)
            return
        else:
            condition = " WHERE BookName LIKE \'%%%s%%\' or Age LIKE \'%%%s%%\' or Author LIKE \'%%%s%%\' or Publish LIKE \'%%%s%%\' or EditStyle LIKE \'%%%s%%\'" % (keyworld,keyworld,keyworld,keyworld,keyworld)
            #print(condition)
            sen = self.query + condition
            try:
                self.sqlQuery.exec(sen)
                self.sqlQuery.last()
                count = self.sqlQuery.at() + 1
                print(count)
            except Exception:
                print(Exception.__str__())
            #print(sen)
            if count == -1 :
                QMessageBox.information(self, "提示", "关键字：\"" + keyworld + "\"查无记录", QMessageBox.Yes)
                return
            else:
                self.totalRecord = count
                self.pages = self.CaculatePages()
                self.ui.labelPages.setText(str(self.pages))
                self.currentPage = 0
                self.SetCurrentPage()
                self.condition = condition
                self.executeQurey(self.currentPage)
                QMessageBox.information(self, "提示", "查询符合关键字：\"" + keyworld + "\"\n共"+str(count)+"条！", QMessageBox.Yes)


            return


    #槽，响应重新载入数据库操作
    def do_reloadDB(self):
        self.condition = ''
        self.totalRecord = self.CaculateTotalRecord()
        self.pages = self.CaculatePages()
        self.ui.labelPages.setText(str(self.pages))
        self.currentPage = 0
        self.SetCurrentPage()
        self.ui.lineEditKeyWorld.setText('')
        self.ui.lineEditGotoPage.setText('')
        self.executeQurey(self.currentPage)