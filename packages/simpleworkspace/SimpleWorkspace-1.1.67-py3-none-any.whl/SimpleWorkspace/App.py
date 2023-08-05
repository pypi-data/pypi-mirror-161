from __future__ import annotations
from logging import Logger
import os as os
import SimpleWorkspace as sw
from SimpleWorkspace.SettingsProviders import SettingsManager_InteractiveConsole
from SimpleWorkspace import LogProviders

class App:
    appName = None
    appCompany = None
    appTitle = None
    appHash = None
    path_currentAppData = ""
    path_currentAppData_storage = None

    logger = None #type: Logger
    settingsManager = None #type: SettingsManager_InteractiveConsole

    @staticmethod
    def Setup(appName, appCompany=None):
        App.appName = appName
        App.appCompany = appCompany
        App.appTitle = appName
        if appCompany != None:
            App.appTitle += " - " + appCompany
        App.path_currentAppData = sw.Path.GetAppdataPath(appName, appCompany)
        App.path_currentAppData_storage = os.path.join(App.path_currentAppData, "storage")
        sw.Directory.Create(App.path_currentAppData_storage)
        
        sw.App.logger = LogProviders.FileLogger.GetLogger( os.path.join(App.path_currentAppData, "info.log"))
        sw.App.settingsManager = SettingsManager_InteractiveConsole(os.path.join(App.path_currentAppData, "config.json"))
        sw.App.settingsManager.LoadSettings()