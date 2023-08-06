import argparse
import random

from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlRecord
from PyQt5.QtCore import QAbstractTableModel, pyqtSignal
from PyQt5.QtGui import QStandardItemModel


class stdQSqlTableModel(QSqlTableModel) :
    """
    table for use with modifying data for a table and subscripotion
    """
    selflags = 0
    selcols = []

    def __init__(self,  selcols : list = None, parent = None):
        super().__init__(parent)


        if selcols is None :
            selcols = []
        else:
            self.selcols = selcols



    def flags(self, index : QModelIndex) :
        """
        required for QTableView
        """

        f = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        if index.column() in self.selcols :
            f = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

        return f


class stdsqlgdr(QObject):
    """
    gdr utility class to Postgres
    """

    currentgrade = None
    tableGdrTemplateName = "stec_gdr_template"
    tableGdrGradeNames = "stec_gdr_names"
    database="vremsoft"

    sigNewSub    = pyqtSignal(str)
    sigNewGrade  = pyqtSignal(str)
    sigDeletedGrade = pyqtSignal(str)
    sigNewData   = pyqtSignal(str,str)


    def __init__(self, user="vremsoft", database="vremsoft", hostname="localhost", port=5432, password="vrem2010!", initTables = False):

        super().__init__()

        self.db = QSqlDatabase.addDatabase("QPSQL")
        self.db.setDatabaseName(database)
        self.db.setHostName(hostname)
        self.db.setPort(int(port))
        self.db.setPassword(password)
        self.db.setUserName(user)
        self.db.setConnectOptions("connect_timeout=5")
        self.db.open()
        
        # In case driver not loaded, here gives hint
        print(self.db.lastError().text())
        self.database = database

        if initTables :
            self.removeAllTables()

        tables = self.db.tables()
        if self.tableGdrTemplateName not in tables:
            self.dropGradeTemplate()

        if self.tableGdrGradeNames not in tables:
            self.dropGradesTable()

    def listToBytes(self, datalist):
        """
        converts a list tp byte stream
        """
        ba = QByteArray()
        stream = QDataStream(ba, QIODevice.WriteOnly)
        l = QVariant(datalist)
        stream.writeQVariant(l)
        return ba

    def byteToList(self, ba):
        """
        byte stream to a list
        """
       # ba = QByteArray(data, len(data) )
        stream = QDataStream(ba, QIODevice.ReadOnly)
        dv = stream.readQVariant()
        return dv


    def removeAllTables(self):
        """
        remove all gdr tables
        """
        tables = self.db.tables()

        query = QSqlQuery(self.db)
        for each in tables :
            if "_gdr_" in each :
                select = "DROP  TABLE  " + each
                try:
                    if not query.exec(select):
                        print("Failed: ", select, query.lastError())

                except:
                    print("Could not ", select)

        self.dropGradeTemplate()
        self.dropGradesTable()


    def loadGradeTemplateCache(self):
        """
        loads the grade template cache
        """
        gradeTemplate = {}

        select = "SELECT * from " + self.tableGdrTemplateName
        query = QSqlQuery(self.db)

        try:
            if not query.exec(select):
                print("Failed: ", select, query.lastError())

        except:
            print("Could not ", select)

        while query.next():

            subname = query.value(0)
            count =  query.value(1)
            gradeTemplate.update({str(subname): int(count)})


        return gradeTemplate

    def loadGrades(self):
        """
        loads grades and returns a list af all the grades
        """
        grades = []
        select = "SELECT * from " + self.tableGdrGradeNames
        query = QSqlQuery(self.db)

        try:
            if not query.exec(select):
                print("Failed: ", select, query.lastError())

        except:
            print("Could not ", select)

        while query.next():
            grade = query.value(0)
            grades.append(grade)

        return grades


    def quoteIt(self,s1):
        """
        simple quote for use with look up by text
        """
        return "'%s'" % s1

    def getNameGradeTables(self, grade = str):

        """
        returns a table for a grade
        """
        grade = str(self.quoteIt(grade))

        select = "SELECT  * from " + self.tableGdrGradeNames  + " where id_grade = " + grade

        query = QSqlQuery(self.db)

        try:
            if query.exec(select) :

                if query.next() :
                    gradename = query.value(0)
                    table = query.value(1)
                    return table

            else:
                print ("Failed:", select, " :", query.lastError())

        except:
            print("Could not ", select)

        return None



    def dropGradeTemplate(self):

        """
        drops the grade template
        """
        select = "DROP  TABLE " + self.tableGdrTemplateName
        query = QSqlQuery(self.db)
        try:
            if not query.exec(select):
                print("Failed: ", select, query.lastError())

        except:
            print("Could not ", select)

        select = "CREATE  TABLE " + self.tableGdrTemplateName + " ( id_subscription TEXT PRIMARY KEY, id_count " \
                                                                "INT NULL, id_data bytea ) "
        try:
            if not query.exec(select) :
                print("Failed: ", select, query.lastError())

        except:
            print("Could not ", select)




    def dropGradesTable(self):
        """
        drop all the grades
        """

        select = "DROP  TABLE  " + self.tableGdrGradeNames
        query = QSqlQuery(self.db)

        try:

            if not query.exec():
                print("Failed: ", select, " :", query.lastError())

        except:
            print("Could not ", select)

        select = "CREATE  TABLE " + self.tableGdrGradeNames + "(id_grade TEXT NOT NULL, id_tablename TEXT, PRIMARY KEY( id_grade ))"

        try:
            if not query.exec(select) :
                print("Failed: ", select, query.lastError())


        except:
            print("Could not ", select)


    def insertIntoGradeTable(self, grade, table):
        """
        inserts a grade into the grade table
        """
        query = QSqlQuery(self.db)
        select = "INSERT INTO " + self.tableGdrGradeNames + "(id_grade , id_tablename ) VALUES ( :id_grade, :id_tablename)"
        query.prepare(select)
        query.bindValue(0, grade)
        query.bindValue(1, table)
        if not query.exec():
            print("Failed: ", select, " :", query.lastError())


    def getEntireGradeTemplate(self):
        """
        gets the entire grade table as a dict
        """
        select = "SELECT * from " + self.tableGdrTemplateName
        query = QSqlQuery(self.db)

        if not query.exec(select):
            print("Failed: ", select, query.lastError())

        data_ = {}
        while query.next():
            sub = query.value(0)
            size = query.value(1)
            b = query.value(2)
            bl = self.byteToList(b)

            if len(bl) > 0:
                data_.update({sub: [size, b]})
                size = len(bl)

            else:
                bl = [0] * size
                b = self.listToBytes(bl)
                data_.update({sub: [size, b]})
        return data_


    def getAllGrades(self):
        select = "SELECT * from " + self.tableGdrGradeNames
        query = QSqlQuery(self.db)

        if not query.exec(select):
            print("Failed: ", select, query.lastError())

        data_ = {}
        while query.next():
            sub = str(query.value(0))
            table = str(query.value(1))
            data_.update( {sub : table})
        return data_



    def copyGradeTempateToGrade(self, table_name):
        query = QSqlQuery(self.db)

        data_ = self.getEntireGradeTemplate()

        select = "CREATE  TABLE " + table_name + " ( id_subscription TEXT PRIMARY KEY, id_count " \
                                                                "INT NULL, id_data bytea ) "

        if not query.exec(select):
                print("Failed: ", select, query.lastError())

        for sub in data_.keys() :

            select = "insert into " + table_name + "( id_subscription, id_count, id_data) VALUES ( :id_subscription, :id_count, :id_data)"
            d = data_[sub]
            size = d[0]
            dt = d[1]

            query.prepare(select)
            query.bindValue(0, QVariant(sub))
            query.bindValue(1, QVariant(size  ))
            query.bindValue(2, QVariant(dt))

            if not query.exec():
                print("Failed: ", select, " :", query.lastError())


    def randomName(self):
        while True :
            name = str(random.random())
            name = name.replace(".","_")
            name = name.replace("-", "_")

            if name is not self.db.tables() :
                return name

    def changeGrade(self, grade : str):

        table_name = self.getNameGradeTables(grade)

        if table_name is None :
            table_name = "stec_gdr_" + self.randomName()

            self.insertIntoGradeTable(grade, table_name)

            if table_name in self.db.tables() :
                query = QSqlQuery(self.db)
                select = "DROP  TABLE " + table_name

                if not query.exec(select):
                    print("Failed: ", select, query.lastError())

            self.copyGradeTempateToGrade(table_name)
            self.sigNewGrade.emit(grade)

    def duplicateGrade(self, oldgrade : str, grade : str):

        table_name = self.getNameGradeTables(grade)
        old_table = self.getNameGradeTables(oldgrade)

        if old_table is None :
            return

        query = QSqlQuery(self.db)

        if table_name is None :
            table_name = "stec_gdr_" + self.randomName()

            self.insertIntoGradeTable(grade, table_name)
            if table_name in self.db.tables() :

                select = "DROP  TABLE " + table_name

                if not query.exec(select):
                    print("Failed: ", select, query.lastError())

            select = "CREATE  TABLE " +  table_name + " AS TABLE " + old_table

            if not query.exec(select):
                print("Failed: ", select, query.lastError())
            else :
                self.sigNewGrade.emit(grade)

    def addSub(self, name: str, count: int, data : list = None):
        self.deleteSub(name)

        if data is None :
            b = self.listToBytes([0] * count)
        else:
            b = self.listToBytes(data)
            count = len(data)

        select = "insert into " + self.tableGdrTemplateName + "( id_subscription, id_count, id_data) VALUES ( :id_subscription, :id_count, :id_data)"
        query = QSqlQuery(self.db)
        query.prepare(select)
        query.bindValue(0, QVariant(name))
        query.bindValue(1, QVariant(count))
        query.bindValue(2, QVariant(b))

        if not query.exec() :
            print("Failed: ", select, " :", query.lastError())
        else:
            self.sigNewSub.emit(name)



    def addSubGrades(self, grades : list = None,  name: str = None, count: int = 1, data : list = None):

        if name is None :
            return

        t = {}
        if grades is None :
            t = self.getAllGrades()


        else:
            for grade in grades :
                table = self.getNameGradeTables(grade)
                if table is not None :
                    t.update( {grade : table})


        grades = t.keys()
        tables = t.values()

        self.deleteSubFromGrades(grades,name)

        for table in tables :
            if data is None :
                b = self.listToBytes([0] * count)
            else:
                b = self.listToBytes(data)
                count = len(data)

            select = "insert into " + table + "( id_subscription, id_count, id_data) VALUES ( :id_subscription, :id_count, :id_data)"
            query = QSqlQuery(self.db)
            query.prepare(select)
            query.bindValue(0, QVariant(name))
            query.bindValue(1, QVariant(count))
            query.bindValue(2, QVariant(b))

            if not query.exec() :
                print("Failed: ", select, " :", query.lastError())
            else:
                self.sigNewSub.emit(name)

    def deleteSubFromGrades(self, grades  : list = None,  name: str = None):

        if name is None:
            return

        t = {}
        if grades is None:
            t = self.getAllGrades()


        else:
            for grade in grades:
                table = self.getNameGradeTables(grade)
                if table is not None:
                    t.update({grade: table})

        for grade in t.keys() :
            table = t.get(grade)


            select = "delete FROM " + table + " WHERE  id_subscription " + " = " + self.quoteIt(name)
            query = QSqlQuery(self.db)

            try:
                if not query.exec(select):
                    print("Failed: ", select, query.lastError())

            except:
                print("Could not ", select)
                return

            if query.next():
                return

    def deleteSub(self, name: str):

        select = "delete FROM " + self.tableGdrTemplateName + " WHERE  id_subscription " + " = " + self.quoteIt(name)
        query = QSqlQuery(self.db)

        try:
            if not query.exec(select):
                print("Failed: ", select, query.lastError())

        except:
            print("Could not ", select)
            return

        if query.next():
            return


    def getGradeInfo(self, grade : str ):

        table_name = self.getNameGradeTables(grade)
        if table_name is None :
            return None
        select = "SELECT * from " + table_name
        query = QSqlQuery(self.db)

        if not query.exec(select):
            print("Failed: ", select, query.lastError())

        data_ = {}
        while query.next():
            sub = query.value(0)
            size = query.value(1)
            b = query.value(2)
            bl = self.byteToList(b)

            if len(bl) > 0:
                data_.update({sub:bl})
                size = len(bl)

            else:
                bl = [0] * size
                b = self.listToBytes(bl)
                data_.update({sub: b})
        return data_

    def deleteGrade(self, grade: str):
        table_name = self.getNameGradeTables(grade)
        query = QSqlQuery(self.db)

        select = "delete from " + self.tableGdrGradeNames + " where id_grade =" + self.quoteIt(grade)

        try:
            if not query.exec(select):
                print("Failed: ", select, query.lastError())
            else:
                self.sigDeletedGrade.emit(grade)

        except:
            print("Could not ", select)
            return

        if query.next():
            print("Here")
        else:
            print("There")


        if table_name is not None :
            select = "DROP  TABLE " + table_name
            try:
                if not query.exec(select):
                    print("Failed: ", select, query.lastError())

            except:
                print("Could not ", select)



    def getGradeTemplateTable(self):
        model = stdQSqlTableModel([0,1])
        model.setTable(self.tableGdrTemplateName)
        model.setEditStrategy(stdQSqlTableModel.OnFieldChange)
        model.select()
        model.setHeaderData(0, Qt.Horizontal, "Subscription ");
        model.setHeaderData(1, Qt.Horizontal, "Number of Elements")
        return model

    def getGradesNamesTable(self):
        model = stdQSqlTableModel([0])
        model.setTable(self.tableGdrGradeNames)
        model.setEditStrategy(stdQSqlTableModel.OnFieldChange)
        model.select()
        model.setHeaderData(0, Qt.Horizontal, "Grade ");
        model.setHeaderData(1, Qt.Horizontal, "Table")
        return model


    def getAnyGradeTable(self, grade : str ):

        table = self.getNameGradeTables(grade)

        if table in self.db.tables() :

            model = stdQSqlTableModel([1],None)
            model.setTable(table)
            model.setEditStrategy(stdQSqlTableModel.OnFieldChange)
            model.select()
            model.setHeaderData(0, Qt.Horizontal, "Grade ");
            model.setHeaderData(1, Qt.Horizontal, "Len")
            model.setHeaderData(2, Qt.Horizontal, "Blob")
            return model
        return None

    def getData(self, grade : str, subscription  : str ):


        table_name = self.getNameGradeTables(grade)

        if table_name is None :
            return None

        s = self.quoteIt(subscription)
        select = "SELECT * from " + table_name  + " WHERE  id_subscription = " + s
        query = QSqlQuery(self.db)

        try:
            if not query.exec(select):
                print("Failed: ", select, query.lastError())

            if query.next():
                sub = query.value(0)

                if sub == subscription:
                    b = query.value(2)
                    bl = self.byteToList(b)
                    return bl
            else:
                print("Failed :", select, " : ", query.lastError())

        except:
            print("Could not ", select)
            return

        return None

    def setData(self,  grade : str, subscription  : str, data : [] ):
        table_name = self.getNameGradeTables(grade)

        if table_name is None:
            return None

        b = self.listToBytes(data)

        s = self.quoteIt(subscription)

        select = "UPDATE " + table_name  + " SET id_data=:id_data WHERE id_subscription = " + s
        query = QSqlQuery(self.db)
        try:
            query.prepare(select)
            query.bindValue(":id_data", QVariant(b))

            if not query.exec() :
                print("Could Not set", select, " : ", query.lastError())
            else:
                self.sigNewGrade.emit(grade,subscription)

        except:
            print("Could not ", select)
            return


    def closeDb(self):
        self.db.close()


class stddatatable(QAbstractTableModel) :

    subName = None
    grade  = None
    gdrExchange = None
    data = []
    model = None


    def __init__(self, gdrExchange : stdsqlgdr, grade : str, subName : str, parent = None):
        super().__init__(parent)

        self.gdrExchange = gdrExchange
        self.grade = grade
        self.subName = subName
        self.data = None
        self.data = self.gdrExchange.getData(self.grade, self.subName)
        self.model = QStandardItemModel(self)

    def isValid(self):
        if self.data is None :
            return True
        return False

    def rowCount(self, parent=QModelIndex()):
        if self.data is None  or len(self.data) == 0 :
            return 0

        return len(self.data)


    def columnCount(self, parent=QModelIndex()) :
        if self.data == None or len(self.data) == 0 :
            return 0
        return 1

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            if i < len(self.data) and len(self.data) > 0 :
                return '{0}'.format(self.data[i])
            else:
                return QVariant()
        else:
            return QVariant()

    def setData(self, index, value,  role=Qt.EditRole ) :
        if self.data is not None and index.isValid() and role == Qt.EditRole :
            if index.column() == 0  and len(self.data) and index.row() < len(self.data) :
                self.data[index.row()] = value
                self.gdrExchange.setData(self.grade, self.subName, self.data)
                self.dataChanged.emit(index,index)
                return True

        return False


    def flags(self, index):
        if self.data is not None and index.row() < len(self.data) :
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return 0

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if section == 0:
                return "Data"
            elif section == 1:
                return "Opos"

        return "oops"

    def insertRows(self, position, rows=1, index=QModelIndex()):
        """ Insert a row into the model. """
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.data.insert(position + row, {"name": "", "address": ""})

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """ Remove a row from the model. """
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.data[position:position + rows]

        self.endRemoveRows()
        return True

    def update(self, data):
        print ('Updating Model')
        self.data = self.gdrExchange.getData(self.grade, self.subName)

        self.layoutAboutToBeChanged.emit()
        self.layoutChanged.emit()


if __name__ == "__main__":

    my_parser = argparse.ArgumentParser(description="Version 1.5.3 Stec Pjanice Python Version")
    # Add the arguments
    my_parser.add_argument('-d', '--host', metavar='host', required=False)

    args = my_parser.parse_args()
    host = args.host

    if host is None:
        host = "localhost"

    postgres2 = stdsqlgdr("vremsoft", "vremsoft", host, 5432, "vrem2010!")

    print("Subs :", postgres2.loadGradeTemplateCache())

    postgres2.addSub("SUB.target_1", 3)

    print("Subs :", postgres2.loadGradeTemplateCache())

    postgres2.changeGrade("gradeABC")

    print("Subs :", postgres2.loadGradeTemplateCache())

    print("B4: ", postgres2.getData("gradeABC", "SUB.target_1"))
    postgres2.setData("gradeABC", "SUB.target_1",[1,2,3,4,5])
    print ("Now: :" , postgres2.getData("gradeABC", "SUB.target_1"))
    jtune = stddatatable(postgres2, "gradeABC", "SUB.target_1")

  #  postgres2.deleteGrade("gradeABC")

    postgres2.closeDb()



