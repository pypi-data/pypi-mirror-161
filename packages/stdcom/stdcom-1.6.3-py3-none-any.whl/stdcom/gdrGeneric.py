import sys, re
import argparse

try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None

from PyQt5.QtWidgets import QDialog, QApplication, QTabWidget, QTableWidgetItem, QCheckBox, QMessageBox
from PyQt5.QtCore import QSettings, QVariant, Qt, QEvent, QSize
from PyQt5.Qt import pyqtSlot, pyqtSignal
from stdcomqt5 import *
from stdcomqt5widget import *
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlRecord
from PyQt5.QtCore import QAbstractTableModel

from gdr import  *
from pjaniceGeneric import  pjaniceGeneric as pj
from stdsqlgdr import  *

class gdrGeneric(QDialog):
    """
    Stec Pjanice Widget, but with trees not list.
    this will turn into a postgres tool..

    """

    aboutToEnter = None
    aboutToLoad = None
    project = "stec-gdr"
    gradeModel : QSqlTableModel = None
    gradeTemplateTable : QSqlTableModel = None
    currentGrade  : str = None
    currentGradeModel : QSqlTableModel = None
    currentDataModel : stddatatable = None
    postgres2 = None
    dbHost = "localhost"
    dbPort =  5432
    dbDbase = "vremsoft"
    dbUser = "vremsoft"
    dbPasswd = "vrem2010!"
    cBridge = None
    currentGradeSubscription = []

    def __init__(self, cBridge: stdcomPyQt = None, project: str = "stec-gdr"):
        """
         def __init__(self, cBridge : stdcomPyQt = None):
        :param cBridge: If you are passing a cBridge and it is controlled here, pass it else it will make one
        """

        self.project = project
        super().__init__()
        self.ui = Ui_GDR()
        self.ui.setupUi(self)
        self.project = project

        self.widgetPjanice =  pj( cBridge, self.project, self.ui.GradeTemplate)
        self.widgetPjanice.setMinimumSize(QtCore.QSize(375, 500))
        self.widgetPjanice.setObjectName("widgetPjanice")
        self.widgetPjanice.setAlternativeIgnore(self.amIUsingSub)
        self.cBridge = self.widgetPjanice.getcBridge()

        self.ui.horizontalLayout_11.addWidget(self.widgetPjanice)
        self.ui.pushButtonAddGrade.clicked.connect(self.addGrade)
        self.ui.pushButtonDuplicate.clicked.connect(self.duplicateGrade)
        self.ui.pushButtonDeleteGrade.clicked.connect(self.deleteGrade)
        self.ui.pushButtonAddSubscription.clicked.connect(self.addTemplateSub)
        self.ui.pushButtonDeleteSubscription.clicked.connect(self.deleteTempateSub)
        self.ui.pushButtonDBAccept.clicked.connect(self.SaveConfig)
        self.ui.pushButtonZero.clicked.connect(self.slotZero)

        self.LoadConfig()
        self.LoadDatabase()

        self.widgetPjanice.sigSelectedData.connect(self.pjaniceSelection)
        self.treeWidgetLoadGrade = stdcomqt5qtreeMorph(self.ui.treeWidgetGrade,[""], self)
        self.treeWidgetLoadGrade.setMinimumSize(QtCore.QSize(0, 400))
        self.treeWidgetLoadGrade.setObjectName("treeWidgetLoadGrade")
        self.ui.verticalLayout_4.addWidget(self.treeWidgetLoadGrade)

        grades = self.postgres2.getAllGrades()
        self.treeWidgetLoadGrade.AddNames(grades)
        self.postgres2.sigNewGrade.connect(self.GradeCreated)

        self.postgres2.sigDeletedGrade.connect(self.GradeDeleted)
        self.treeWidgetLoadGrade.newTextSignal.connect(self.TreeGradeSelected)
        self.ui.pushButtonLoadGrade.clicked.connect(self.UpLoadGrade)

    def getCount(self):
        """
        get the display counts
        """
        cnt = self.ui.spinBoxNumberItems.value()
        return cnt

    def LoadDatabase(self):
        """
        load the database, this is set to a postgres database
        """
        if self.postgres2 is not None :
            self.postgres2.closeDb()
            self.postgres2.deleteLater()

        self.postgres2 = stdsqlgdr(self.dbUser, self.dbDbase, self.dbHost, self.dbPort, self.dbPasswd)

        if self.gradeTemplateTable is not None :
            self.gradeTemplateTable.deleteLater()
        self.gradeTemplateTable = self.postgres2.getGradeTemplateTable()
        self.ui.tableViewGradeTemplate.setModel(self.gradeTemplateTable)

        if  self.gradeModel is not None :
            self.gradeModel.deleteLater()
        self.gradeModel = self.postgres2.getGradesNamesTable()
        self.ui.tableViewGrades.setModel(self.gradeModel)

        self.ui.tableViewGrades.clicked.connect(self.gradeSelected)
        self.ui.tableViewGradeEdit.clicked.connect(self.subSelection)
        self.ui.tableViewGradeEditData.setSortingEnabled(False)
        self.ui.tableViewGradeEditData.setShowGrid(True)

        self.currentGrade = None
        if self.currentDataModel is not None:
            self.currentDataModel.deleteLater()
        self.ui.tableViewGradeEditData.setModel(None)
        self.ui.lineEditCurrentSub.clear()

        if self.currentGradeModel is not None:
            self.currentGradeModel.deleteLater()
            self.currentGradeModel = None
            self.ui.tableViewGradeEdit.setModel(None)

    @pyqtSlot()
    def SaveConfig(self):
        """
        saves the configurations, this is not to the database, because it needs the information
        of where the database is.. so it is just normal ini QSettings stuff
        """
        settings = VSettings(self.project)
        self.dbHost = self.ui.lineEditHost.text()
        self.dbPort = int(self.ui.lineEditPort.text())
        self.dbUser = self.ui.lineEditUser.text()
        self.dbDbase = self.ui.lineEditDatabase.text()
        self.dbPasswd = self.ui.lineEditPassword.text()

        settings.setValue('PostgresHostname', self.dbHost)
        settings.setValue('PostgresPort', self.dbPort)
        settings.setValue('PostgresUser', self.dbUser)
        settings.setValue('PostgresDbase', self.dbDbase)
        settings.setValue('PostgresPasswd', self.dbPasswd)
        settings.sync()
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("You will need to Exit and Restart this Application")
        msgBox.setWindowTitle("Postgres Changed")
        msgBox.setStandardButtons(QMessageBox.Ok)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')

        self.LoadDatabase()

    def amIUsingSub(self, name : str):
        """
        if pjanice wants to delete a sub when done, it must ask us if it is ok
        """
        if name in self.currentGradeSubscription :
            return True

        return False

    def LoadConfig(self):
        """
        Loads an ini using QSetting for this project
        """
        settings = VSettings(self.project)
        self.dbHost = str(settings.value('PostgresHostname', self.dbHost))
        self.dbPort = int (settings.value('PostgresPort', self.dbPort))
        self.dbUser = str(settings.value('PostgresUser', self.dbUser))
        self.dbDbase = str(settings.value('PostgresDbase', self.dbDbase))
        self.dbPasswd = str(settings.value('PostgresPasswd', self.dbPasswd))

        self.ui.lineEditHost.setText(self.dbHost)
        self.ui.lineEditPort.setText( str(self.dbPort))
        self.ui.lineEditUser.setText(self.dbUser)
        self.ui.lineEditDatabase.setText(self.dbDbase)
        self.ui.lineEditPassword.setText( self.dbPasswd)


    @pyqtSlot()
    def addGrade(self):
        """
        Adds a grade
        """
        print ("Add Grade")
        text = self.ui.editlineGrade.text()
        if text is not None and text !=  "" :
            self.postgres2.changeGrade(text)
            self.gradeModel.deleteLater()
            self.gradeModel = self.postgres2.getGradesNamesTable()
            self.ui.tableViewGrades.setModel(self.gradeModel)
            self.ui.editlineGrade.clear()

    @pyqtSlot()
    def duplicateGrade(self):
        """
        duplicated an exisitng grade
        """
        print("Duplicated Grade")
        text = self.ui.editlineGrade.text()

        if text is not None and text != "" and  self.currentGrade is not None and self.currentGrade != "":
            oldgrade  = self.currentGrade
            self.postgres2.duplicateGrade(oldgrade,text)
            self.gradeModel.deleteLater()
            self.gradeModel = self.postgres2.getGradesNamesTable()
            self.ui.tableViewGrades.setModel(self.gradeModel)
            self.ui.editlineGrade.clear()


    @pyqtSlot()
    def deleteGrade(self):
        """
        deletes a grade
        """
        indices = self.ui.tableViewGrades.selectionModel().selectedRows()
        rows = []
        for index in indices:
            row = index.row()
            if row < self.gradeModel.rowCount() :
                rec = self.gradeModel.record(row)
                text = str(rec.value(0))
                rows.append(text)

        for grade in rows :
            self.postgres2.deleteGrade(grade)

        self.gradeModel.deleteLater()
        self.gradeModel = self.postgres2.getGradesNamesTable()
        self.ui.tableViewGrades.setModel(self.gradeModel)
        self.currentGrade = None
        self.ui.lineEditCurrentGrade.clear()


        if self.currentDataModel is not None:
            self.currentDataModel.deleteLater()
        self.ui.tableViewGradeEditData.setModel(None)
        self.ui.lineEditCurrentSub.clear()

        if self.currentGradeModel is not None:
            self.currentGradeModel.deleteLater()
            self.currentGradeModel = None
            self.ui.tableViewGradeEdit.setModel(None)



    @pyqtSlot()
    def deleteTempateSub(self):
        """
        deletes a grade from template and also all grades if selected to do this
        """
        indices = self.ui.tableViewGradeTemplate.selectionModel().selectedRows()
        rows = []
        for index in indices:
            row = index.row()
            if row < self.gradeTemplateTable.rowCount():
                rec = self.gradeTemplateTable.record(row)
                text = str(rec.value(0))
                rows.append(text)

        checked = self.ui.checkBoxAlsoAddToGrades.isChecked()
        for sub in rows:
            self.postgres2.deleteSub(sub)
            if checked :
                self.postgres2.deleteSubFromGrades(None,sub)

        self.gradeTemplateTable.select()

        if self.currentGradeModel is not None:
            self.currentGradeModel.select()

        self.ui.editlineSubscription.clear()
        self.ui.lineEditValuesToEnter.clear()
        self.aboutToEnter = None


    @pyqtSlot()
    def addTemplateSub(self):
        """
        adds a subscription to a template and also to the grades if selected
        """
        text = self.ui.editlineSubscription.text()
        if text is not None and text != "":
            count = self.getCount()

            if self.aboutToEnter is None :
                data = [0] * count

            else:
                data = list(self.aboutToEnter)

            self.postgres2.addSub(text, count, data)
            self.gradeTemplateTable.select()

            checked = self.ui.checkBoxAlsoAddToGrades.isChecked()
            if checked :
                self.postgres2.addSubGrades(None, text, count, data )
                if self.currentGradeModel is not  None :
                    self.currentGradeModel.select()


            self.ui.editlineSubscription.clear()
            self.ui.lineEditValuesToEnter.clear()
            self.aboutToEnter = None


    def gradeSelected(self, item):
        """
        if someone selects a grade item from table view
        """
        col = item.column()

        if col == 0 :
            self.currentGrade = item.data()

            self.ui.lineEditCurrentGrade.setText(self.currentGrade)

            if self.currentGradeModel is not None :
                self.currentGradeModel.deleteLater()
                self.currentGradeModel = None



            self.currentGradeModel = self.postgres2.getAnyGradeTable(self.currentGrade)


            if self.currentGradeModel is not None :
                self.ui.tableViewGradeEdit.setModel(self.currentGradeModel)
                self.ui.editlineGrade.setText(self.currentGrade)


            self.ui.tableViewGradeEditData.setModel(None)


    def subSelection(self, item):
        """
        if subscrition is selected from the grade edit table
        """
        col = item.column()

        if col == 0 :
            subcription = str(item.data())

            print(subcription)
            if self.currentGrade is not None and subcription != " " :
                if self.currentDataModel is not None :
                    self.currentDataModel.deleteLater()

                self.currentDataMode = stddatatable(self.postgres2, self.currentGrade, subcription)
                self.ui.tableViewGradeEditData.setModel(self.currentDataMode)
                self.ui.lineEditCurrentSub.setText(subcription)
                header = self.ui.tableViewGradeEditData.horizontalHeader()
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        else :
            if self.currentDataModel is not None:
                self.currentDataModel.deleteLater()
            self.ui.tableViewGradeEditData.setModel(None)
            self.ui.lineEditCurrentSub.clear()

    @pyqtSlot(str, list)
    def pjaniceSelection (self, name, data) :
        """
        if pjanice selects a live subscription
        """
        print ("Pjanice Selection", name, data)
        nbr = len(data)
        self.ui.spinBoxNumberItems.setValue(nbr)
        self.ui.editlineSubscription.setText(name)
        self.aboutToEnter = data
        uData = ','.join(map(str, data))
        self.ui.lineEditValuesToEnter.setText(uData)

    @pyqtSlot()
    def slotZero(self):
        """
        if user zeros out a subsription in the template, this can be useful, if the value is not known of what to put in the
        subscriptiopn for that grade yet
        """
        self.aboutToEnter = None
        self.ui.lineEditValuesToEnter.clear()
        data = ['0'] * self.getCount()
        uData = ','.join(map(str, data))
        self.ui.lineEditValuesToEnter.setText(uData)

    @pyqtSlot()
    def UpLoadGrade(self):
        """
        Upload a grade to the real Multiverse platform
        """
        if self.aboutToEnter is not None :

            data = self.postgres2.getGradeInfo(self.aboutToEnter )
            print("Load Grade", self.aboutToEnter, data)
            self.currentGradeSubscription = data.keys()
            for each in self.currentGradeSubscription :
                d = list(data.get(each))
                self.cBridge.subscribe(str(each))
                self.cBridge.writeValues(each, d)

    @pyqtSlot(str,str)
    def TreeGradeSelected(self, grade, desc):
        print("TreeGrade", grade)
        self.aboutToEnter = grade

    @pyqtSlot(str)
    def GradeCreated(self,grade):
        print("New Grade", grade )

    @pyqtSlot(str)
    def GradeDeleted(self, grade):
        print("Deleted Grade", grade)




if __name__ == "__main__":
    """
    bumped version
    """

    my_parser = argparse.ArgumentParser( description="Version 1.6.2 Stec Pjanice Python Version")
    # Add the arguments
    my_parser.add_argument('-p','--project', metavar='project', required=False)


    args = my_parser.parse_args()
    nextProject = args.project

    app = QApplication(sys.argv)
    if nextProject is not None :
        window = gdrGeneric(None,nextProject)
    else:
        window = gdrGeneric()

    window.setWindowTitle("Stec PJanice Viewer")

    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec_()
    if window.widgetPjanice.cBridge != None:
        window.widgetPjanice.cBridge.terminate()


