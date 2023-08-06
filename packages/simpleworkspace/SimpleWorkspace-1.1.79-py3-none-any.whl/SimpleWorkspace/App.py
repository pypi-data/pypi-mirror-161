from __future__ import annotations
from logging import Logger
import os as os
import SimpleWorkspace as sw
from SimpleWorkspace.SettingsProviders import SettingsManager_InteractiveConsole
from SimpleWorkspace import LogProviders

class App:
    appName = None
    appCompany = None
    appTitle = None #example: "appname - appcompany"
    appHash = 0 #appname + appcompany hashed together, numeric hash
    path_currentAppData = ""            #windows example: 'C:\\Users\\username\\AppData\\Roaming\\AppCompany\\AppName'
    path_currentAppData_storage = None  #windows example: 'C:\\Users\\username\\AppData\\Roaming\\AppCompany\\AppName\\Storage'

    _loggerFilepath = None
    logger = None #type: Logger
    settingsManager = None #type: SettingsManager_InteractiveConsole

    @staticmethod
    def Setup(appName, appCompany=None):
        App.appName = appName
        App.appCompany = appCompany
        App.appTitle = appName
        if appCompany != None:
            App.appTitle += " - " + appCompany
        App.appHash = hash(App.appTitle)

        App.path_currentAppData = sw.Path.GetAppdataPath(appName, appCompany)
        App.path_currentAppData_storage = os.path.join(App.path_currentAppData, "storage")
        sw.Directory.Create(App.path_currentAppData_storage)
        
        sw.App._loggerFilepath = os.path.join(App.path_currentAppData, "info.log")
        sw.App.logger = LogProviders.RotatingFileLogger.GetLogger( sw.App._loggerFilepath)

        sw.App.settingsManager = SettingsManager_InteractiveConsole(os.path.join(App.path_currentAppData, "config.json"))
        sw.App.settingsManager.LoadSettings()