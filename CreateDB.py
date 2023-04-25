from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtSql import QSqlDatabase

#数据库单例模式，保证链接数据库实例仅有一个。
class SingleDBConnect(object):
    _instance = None
    DB = None
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance
    def __init__(self):
        if self.DB:
            return
        try:
            self.DB = QSqlDatabase.addDatabase("QSQLITE")
            self.DB.setDatabaseName("DB/MTSongZaiDB.db")
            #记得打开数据库哦
            self.DB.open()
            print("Open DB success!")
        except Exception as e:
            QMessageBox.critical(self, "错误", "数据库驱动错误")
            #print(e)

if __name__ == '__main__':
    db1 = SingleDBConnect()
    db2 = SingleDBConnect()

    print(id(db1))
    print(id(db2))