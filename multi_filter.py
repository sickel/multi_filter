# -*- coding: utf-8 -*-
"""
/***************************************************************************
 multiFilter
                                 A QGIS plugin
 Set filter on multiple selected layers
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-03-22
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Morten Sickel
        email                : morten@sickel.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt 
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction, QInputDialog, QListWidgetItem
from qgis.core import QgsProject, QgsSettings
# Initialize Qt resources from file resources.py
from .resources import *
import json

# Import the code for the DockWidget
from .multi_filter_dockwidget import multiFilterDockWidget
import os.path

class multiFilter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'multiFilter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Multifilter')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'multiFilter')
        self.toolbar.setObjectName(u'multiFilter')

        #print "** INITIALIZING multiFilter"

        self.pluginIsActive = False
        self.dockwidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('multiFilter', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/multi_filter/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Multifilter'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING multiFilter"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD multiFilter"

        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Multifilter'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True
            #print "** STARTING multiFilter"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = multiFilterDockWidget()
                self.dockwidget.tbAdd.clicked.connect(self.addLayer)
                self.dockwidget.tbRemove.clicked.connect(self.removeLayer)
                self.dockwidget.pBFilter.clicked.connect(self.filterlayers)
                self.dockwidget.pBClear.clicked.connect(self.clearfilters)
                self.dockwidget.tbCopy.clicked.connect(self.copyfilter)
            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            s = QgsSettings()
            print('reading ----')
            settings = s.value('multi_filter/setup', None)
            print(settings)
            if not settings is None:
                guidata = json.loads(settings)
                if self.dockwidget.lwLayers.count() == 0: # No data in list, needs to rebuild
                    for id in guidata['layers']:
                        layer = QgsProject.instance().mapLayer(id)
                        if not layer is None:
                            self.addLayerToList(layer)
                    self.dockwidget.pTEFiltertext.appendPlainText(guidata['filter'])
            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()  
            
    def addLayer(self):
        #text, ok = QInputDialog.getText(self.dockwidget, 'Add a New Wish', 'New Wish:')
        layer = self.dockwidget.mMCLLayers.currentLayer()
        #todo: check if layer already is in widgetlist
        self.addLayerToList(layer)
    
    def addLayerToList(self,layer):
        id = layer.id()
        newItem = QListWidgetItem()
        newItem.setText(layer.name())
        newItem.setData(Qt.UserRole,{'id':id})
        self.dockwidget.lwLayers.addItem(newItem)
        self.storelayers()
        
    def removeLayer(self):
        current_row = self.dockwidget.lwLayers.currentRow()
        if current_row >= 0:
            current_item = self.dockwidget.lwLayers.takeItem(current_row)
            del current_item 
        self.storelayers()
        
    def filterlayers(self):
        """ Applies the filter in the text edit box to all layers """
        filtertext = self.dockwidget.pTEFiltertext.toPlainText()
        print(filtertext)
        self.setfilter(filtertext)
   
    def setfilter(self,filtertext):
        """ Applies filtertext to all selected layers 
        :param filtertext: The text to use as a filter, may be '' to remove filtering.
        :type filtertext: String
        """
        self.storelayers()
        listwdg = self.dockwidget.lwLayers
        for i in range(listwdg.count()):
            item = listwdg.item(i)
            item.setBackground(QColor('#FFFFFF'))
            layername = item.text()
            print(layername)
            itemdata = item.data(Qt.UserRole)
            layer = QgsProject.instance().mapLayer(itemdata['id'])
            if not layer is None:
                try:
                    print(f"Filtering {layername}")
                    # layer = QgsProject.instance().mapLayersByName(layername)[0]
                    if not layer.setSubsetString(filtertext):
                        print(f'Cannot filter {layername}')
                        item.setBackground(QColor('#ff5566'))
                        # TODO set bgcolor
                except:
                    #TODO mark layer in itemlist
                    print(f'Cannot filter {layername}')
            else:
                item.setBackground(QColor('#777'))
            
    def clearfilters(self):
        """ Clears filters for all layers"""
        print('Clearing filters')
        self.setfilter('')

    def copyfilter(self):
        """ Copies the filter from the selected layer(s) to the filter edit area """
        
        items = self.dockwidget.lwLayers.selectedItems()
        if len(items) > 0:
            for item in items:
                itemdata = item.data(Qt.UserRole)
                filter = itemdata['layer'].subsetString()
                if filter > '':
                    self.dockwidget.pTEFiltertext.appendPlainText(filter)
                    
                
    def storelayers(self):
        """ Stores the current layers and filter expression to be able to
        get it back when the project is reopened """
        layerset = []
        listwdg = self.dockwidget.lwLayers
        for i in range(listwdg.count()):
            item = listwdg.item(i)
            itemdata = item.data(Qt.UserRole)
            layerset.append(itemdata['id'])
        filtertext = self.dockwidget.pTEFiltertext.toPlainText()
        storedata = json.dumps({'filter': filtertext, 'layers' : layerset})
        print("Writing:")
        print(storedata)
        s = QgsSettings()
        s.setValue('multi_filter/setup', storedata)