# coding: utf-8

import sys

import solvergui.preferencesDlg, solvergui.compositionView
from solvergui.includes import *
from solvergui.viewportManager import *
from solvergui.prototypeObjects import PrototypeManager
from solvergui.tools import *
from solvergui.panel import *
from solvergui.solutionView import *
from solvergui.parameters import Settings
from geosolver.randomproblem import random_triangular_problem_3D

from solvergui.ui_randomProblemDialog import Ui_randomProblemDialog

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(QtWidgets.QMainWindow):
    # Ui_MainWindow: creation of the main window with al its content
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.setWindowTitle(self.tr("Geometric Constraint Solver"))
        self.activatedTool = None
        self.settings = Settings()
        self.saveFileName = ""
        self.createViewportManager()
        self.createDecompositionView()
        self.createSolutionView()
        self.createActions()
        self.createTriggers()
        self.createPanel()
        self.createMenus()
        self.createStatusBar()
        self.createToolbar()

        self.resize(QtCore.QSize(QtCore.QRect(0, 0, 800, 600).size()).expandedTo(self.minimumSizeHint()))

    def createActions(self):
        # the actions which the user can select from the menu
        self.actionNew = QtWidgets.QAction(self.tr("&New"), self)
        self.actionNew.setShortcut(self.tr("Ctrl+N"))
        self.actionOpen = QtWidgets.QAction(self.tr("&Open"), self)
        self.actionOpen.setShortcut(self.tr("Ctrl+O"))
        self.actionSave = QtWidgets.QAction(self.tr("&Save"), self)
        self.actionSave.setShortcut(self.tr("Ctrl+S"))
        self.actionSave_As = QtWidgets.QAction(self.tr("Save &As .."), self)
        self.actionSave_As.setShortcut(self.tr("Ctrl+A"))
        self.actionImport = QtWidgets.QAction(self.tr("&Import"), self)
        self.actionImport.setShortcut(self.tr("Ctrl+I"))
        self.actionClose = QtWidgets.QAction(self.tr("&Close"), self)
        self.actionClose.setShortcut(self.tr("Ctrl+C"))
        self.actionQuit = QtWidgets.QAction(self.tr("E&xit"), self)
        self.actionQuit.setShortcut(self.tr("Ctrl+X"))
        # Rick 20090522
        self.actionGenerate = QtWidgets.QAction(self.tr("&Generate"), self)
        self.actionGenerate.setShortcut(self.tr("Ctrl+G"))

        self.editGroup = QtWidgets.QActionGroup(self)
        self.editGroup.setExclusive(True)
        self.actionSelect = QtWidgets.QAction(self.tr("Select"), self)
        self.actionSelect.setCheckable(True)
        self.actionPlacePoint = QtWidgets.QAction(self.tr("Point"), self)
        self.actionPlacePoint.setCheckable(True)
        self.actionMove = QtWidgets.QAction(self.tr("Move"), self)
        self.actionMove.setCheckable(True)
        self.actionConnect = QtWidgets.QAction(self.tr("Connect"), self)
        self.actionConnect.setCheckable(True)
        self.actionDistanceConstraint = QtWidgets.QAction(self.tr("Distance"), self)
        self.actionDistanceConstraint.setCheckable(True)
        self.actionDistance = QtWidgets.QAction(self.tr("Line"), self)
        self.actionDistance.setCheckable(True)
        self.actionAngleConstraint = QtWidgets.QAction(self.tr("Angle"), self)
        self.actionAngleConstraint.setCheckable(True)
        self.actionFixedConstraint = QtWidgets.QAction(self.tr("Fixed"), self)
        self.actionFixedConstraint.setCheckable(True)

        self.actionMinMaxView = QtWidgets.QAction(self.tr("MM"), self)
        self.actionSolve = QtWidgets.QAction(self.tr("Solve"), self)
        self.actionClusters = QtWidgets.QAction(self.tr("Clusters"), self)

        self.editGroup.addAction(self.actionSelect)
        self.editGroup.addAction(self.actionPlacePoint)
        self.editGroup.addAction(self.actionMove)
        self.editGroup.addAction(self.actionConnect)
        self.editGroup.addAction(self.actionDistanceConstraint)
        self.editGroup.addAction(self.actionAngleConstraint)
        self.editGroup.addAction(self.actionDistance)
        self.editGroup.addAction(self.actionFixedConstraint)

        self.actionCompositionView = QtWidgets.QAction(self.tr("Composition View"), self)
        self.actionSolutionView = QtWidgets.QAction(self.tr("Solution View"), self)
        self.actionPreferences = QtWidgets.QAction(self.tr("Preferences"), self)

    def createAction(self, text, slot=None, signal='triggered'):
        action = QAction(text, self)
        signal_dict = {'triggered': action.triggered, 'changed': action.changed,
                       'toggled': action.toggled, 'hovered': action.hovered}
        if slot is not None:
            # self.connect(action, SIGNAL(signal), slot)
            signal_dict[signal].connect(slot)
        return action

    def createTriggers(self):
        # # menu actions
        self.actionNew.triggered.connect(self.new)
        self.actionQuit.triggered.connect(self.close)
        self.actionSave.triggered.connect(self.save)
        self.actionSave_As.triggered.connect(self.saveAs)
        self.actionImport.triggered.connect(self.importFile)
        self.actionOpen.triggered.connect(self.load)
        #
        self.actionCompositionView.triggered.connect(self.showCompositionView)
        self.actionSolutionView.triggered.connect(self.showSolutionView)
        self.actionPreferences.triggered.connect(self.showPreferencesDlg)
        #
        self.actionSelect.changed.connect(self.selectTriggered)
        self.actionPlacePoint.changed.connect(self.placePointTriggered)
        self.actionMove.changed.connect(self.moveTriggered)
        self.actionConnect.changed.connect(self.connectTriggered)
        self.actionDistanceConstraint.changed.connect(self.distanceConstraintTriggered)
        self.actionMinMaxView.triggered.connect(self.viewportManager.minmaxView)
        #
        self.actionSolve.triggered.connect(PrototypeManager().solve)
        self.actionSolve.triggered.connect(self.compositionView.createDecomposition)
        self.actionSolve.triggered.connect(self.solutionView.createSolution)
        self.actionSolve.triggered.connect(self.viewportManager.updateSolution)
        self.actionSolve.triggered.connect(self.viewportManager.updateDecomposition)
        self.actionSolve.triggered.connect(self.viewportManager.updateViewports)
        self.actionSolve.triggered.connect(self.updateConstraintInfo)
        #
        self.actionClusters.triggered.connect(self.showClusters)
        self.actionDistance.changed.connect(self.placeDistanceTriggered)
        self.actionAngleConstraint.changed.connect(self.placeAngleConstraintTriggered)
        self.actionFixedConstraint.changed.connect(self.placeFixedConstraintTriggered)
        # # Rick 20090522
        # QtCore.QObject.connect(self.actionGenerate,QtCore.SIGNAL("triggered()"),self.generateRandom)

    def createMenus(self):
        # connect the defined actions with menu items
        self.menuFile = self.menuBar().addMenu(self.tr("&File"))
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionGenerate)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)

        self.menuView = self.menuBar().addMenu(self.tr("&View"))
        self.menuView.addAction(self.actionCompositionView)
        self.menuView.addAction(self.actionSolutionView)

        self.menuWindow = self.menuBar().addMenu(self.tr("&Window"))
        self.menuWindow.addAction(self.dock.toggleViewAction())
        self.menuWindow.addSeparator()
        self.menuWindow.addAction(self.actionPreferences)

        self.menuHelp = self.menuBar().addMenu(self.tr("&Help"))

    def createStatusBar(self):
        # set the statusbar
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.statusSolveInfo = QtWidgets.QLabel("")
        self.statusbar.addPermanentWidget(self.statusSolveInfo)
        self.setStatusBar(self.statusbar)

    def createToolbar(self):
        self.toolbar = QtWidgets.QToolBar("edit actions", self)
        self.toolbar.addAction(self.actionSelect)
        self.toolbar.addAction(self.actionPlacePoint)
        self.toolbar.addAction(self.actionMove)
        self.toolbar.addAction(self.actionConnect)
        self.toolbar.addAction(self.actionDistanceConstraint)
        self.toolbar.addAction(self.actionAngleConstraint)
        self.toolbar.addAction(self.actionDistance)
        self.toolbar.addAction(self.actionFixedConstraint)
        self.toolbar.addAction(self.actionMinMaxView)
        self.toolbar.addAction(self.actionSolve)
        self.toolbar.addAction(self.actionClusters)
        self.toolbar.insertSeparator(self.actionMinMaxView)
        self.toolbar.insertSeparator(self.actionSolve)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)

    def createViewportManager(self):
        self.viewportManager = ViewportManager(self)
        self.viewportManager.showViewport(DisplayViewport.ALL, None)
        self.updateTool = UpdateToolCommand(self.viewportManager)

    def createPanel(self):
        self.dock = QtWidgets.QDockWidget(self.tr("Prototypes"), self)
        self.maxWidth = self.dock.maximumWidth()
        self.dock.setMaximumWidth(240)
        self.dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.infoPanel = Panel(self, self.dock)
        self.dock.setWidget(self.infoPanel)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock)

    def createDecompositionView(self):
        self.compositionView = CompositionView(None, self.viewportManager, ViewportType.DECOMPOSITION ,PrototypeManager())

    def createSolutionView(self):
        self.solutionView = SolutionView(self, self.viewportManager, ViewportType.SOLUTION ,PrototypeManager())

        #self.viewPanelSplitter.setSizes([400, 200])

    def updateWindow(self):
        self.viewportManager.updateViewports()

    def showCompositionView(self):
        self.compositionView.show()

    def showSolutionView(self):
        self.solutionView.show()

    def updateConstraintInfo(self):
        self.infoPanel.reset()
        updateTaskbarCommand = UpdateTextInTaskbarCommand(PrototypeManager(), self)
        updateTaskbarCommand.execute()

    def showClusters(self):
        prtManager = PrototypeManager()
        prtManager.showClusters()
        self.viewportManager.updateViewports()

    def showPreferencesDlg(self):
        self.preferencesDlg = preferencesDlg.PreferencesDlg(self.viewportManager)
        self.preferencesDlg.exec_()

    def selectTriggered(self):
        if self.actionSelect.isChecked():
            self.updateTool.execute(SelectTool())

    def placePointTriggered(self):
        if self.actionPlacePoint.isChecked():
            self.updateTool.execute(PlacePointTool())

    def distanceConstraintTriggered(self):
        if self.actionDistanceConstraint.isChecked():
            self.updateTool.execute(PlaceDistanceConstraintTool())

    def moveTriggered(self):
        if self.actionMove.isChecked():
            self.updateTool.execute(MoveTool())

    def connectTriggered(self):
        if self.actionConnect.isChecked():
            self.updateTool.execute(ConnectTool())

    def placeDistanceTriggered(self):
        if self.actionDistance.isChecked():
            self.updateTool.execute(PlaceDistanceTool())

    def placeFixedConstraintTriggered(self):
        if self.actionFixedConstraint.isChecked():
            self.updateTool.execute(PlaceFixedConstraintTool())

    def placeAngleConstraintTriggered(self):
        if self.actionAngleConstraint.isChecked():
            self.updateTool.execute(PlaceAngleConstraintTool())

    def new(self):
        result = QtWidgets.QMessageBox.warning(self, self.tr("New Scene"),
                                               self.tr("The scene may have been modified.\n" "Do you want to save your changes?"),
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Yes)
        if result == QtWidgets.QMessageBox.Yes:
            self.save()
        elif result == QtWidgets.QMessageBox.Cancel:
            return

        self.newCommand = ClearSceneCommand(self)
        self.newCommand.execute()
        self.setWindowTitle(self.tr("Geometric Constraint Solver"))

    def load(self):
        result = QtWidgets.QMessageBox.warning(self, self.tr("Scene Changes"), self.tr("The scene may have been modified.\n" "Do you want to save your changes?"), \
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Yes)
        if result == QtWidgets.QMessageBox.Yes:
            self.save()
        elif result == QtWidgets.QMessageBox.Cancel:
            return

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            self.tr("Open File"),
                                                            "",
                                                            self.tr("GCS Files (*.gcs)"))
        if filename:
            self.newCommand = ClearSceneCommand(self)
            self.newCommand.execute()
            self.saveFileName = filename
            self.loadCommand = LoadCommand(self)
            self.loadCommand.execute(self.saveFileName)
            nameForTitle = self.saveFileName
            from os.path import basename
            title = basename(nameForTitle)
            # title = nameForTitle.remove(0, nameForTitle.lastIndexOf("/")+1)
            self.setWindowTitle("- " + title + self.tr(" - Geometric Constraint Solver"))

    def save(self):
        if not self.saveFileName:
            self.saveAs()
        else:
            self.saveCommand = SaveCommand(self)
            self.saveCommand.execute(self.saveFileName)
            nameForTitle = self.saveFileName
            from os.path import basename
            title = basename(nameForTitle)
            # title = nameForTitle.remove(0, nameForTitle.lastIndexOf("/")+1)
            self.setWindowTitle("- " + title + self.tr(" - Geometric Constraint Solver"))

    def saveAs(self):
        saveDialog = QtWidgets.QFileDialog()
        saveDialog.setDefaultSuffix(".gcs")
        filename = saveDialog.getSaveFileName(self,
                                              self.tr("Save As.."),
                                              "",
                                              self.tr("GCS Files (*.gcs)"))

        if filename:
            if not filename.endswith(saveDialog.defaultSuffix()):
                filename.append(saveDialog.defaultSuffix())
            self.saveFileName = filename
            self.save()

    def importFile(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         self.tr("Import File"),
                                                         "",
                                                         self.tr("GCS Files (*.gcs)"))
        if filename:
            self.importCommand = ImportCommand(self)
            self.importCommand.execute(filename)

    # Rick 20090522
    def generateRandom(self):
        # # first do as if File->New was selected
        self.new()
        # # then show randomProblemDialog
        # ui = Ui_randomProblemDialog()
        # dialog = QtDialog()
        # # create random problem
        (numpoints, ratio, size, rounding) = (10, 0.0, 100.0, 0.0)
        problem = random_triangular_problem_3D(numpoints, size, rounding, ratio)
        prototypeManager = PrototypeManager()
        prototypeManager.setProblem(problem)
        self.viewportManager.updateViewports()
        # # set window title
        # title = "Untitled"
        # self.setWindowTitle(title + self.tr(" - Geometric Constraint Solver"))

    def tr(self, string):
        return QtWidgets.QApplication.translate("Ui_MainWindow", string, None)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
