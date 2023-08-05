from __future__ import annotations as _annotations
from SimpleWorkspace import ConsoleHelper as _ConsoleHelper
import os as _os
import json as _json
import SimpleWorkspace as _sw


class SettingsManager:
    _settingsPath = None
    __Command_Delete = "#delete"
    Settings = {}

    @staticmethod
    def LoadSettings():
        SettingsManager.Settings = {}
        if not (_os.path.exists(SettingsManager._settingsPath)):
            return
        if _os.path.getsize(SettingsManager._settingsPath) == 0:
            return
        try:
            SettingsManager.Settings = _json.loads(_sw.File.Read(SettingsManager._settingsPath))
        except Exception as e:
            _os.rename(SettingsManager._settingsPath, SettingsManager._settingsPath + ".bak")
        return SettingsManager.Settings

    @staticmethod
    def SaveSettings():
        jsonData = _json.dumps(SettingsManager.Settings)
        _sw.File.Create(SettingsManager._settingsPath, jsonData)

    @staticmethod
    def __Console_ChangeSettings():
        while True:
            _ConsoleHelper.ClearConsoleWindow()
            _ConsoleHelper.LevelPrint(0, "[Change Settings]")
            _ConsoleHelper.LevelPrint(1, "0. Save Settings and go back.(Type cancel to discard changes)")
            _ConsoleHelper.LevelPrint(1, "1. Add a new setting")
            _ConsoleHelper.LevelPrint(2, "[Current Settings]")
            dictlist = []
            dictlist_start = 2
            dictlist_count = 2
            for key in SettingsManager.Settings:
                _ConsoleHelper.LevelPrint(3, str(dictlist_count) + ". " + key + " : " + SettingsManager.Settings[key])
                dictlist.append(key)
                dictlist_count += 1
            _ConsoleHelper.LevelPrint(1)
            choice = input("-Choice: ")
            if choice == "cancel":
                SettingsManager.LoadSettings()
                _ConsoleHelper.AnyKeyDialog("Discarded changes!")
                break
            if choice == "0":
                SettingsManager.SaveSettings()
                _ConsoleHelper.LevelPrint(1)
                _ConsoleHelper.AnyKeyDialog("Saved Settings!")
                break
            elif choice == "1":
                _ConsoleHelper.LevelPrint(1, "Setting Name:")
                keyChoice = _ConsoleHelper.LevelInput(1, "-")
                _ConsoleHelper.LevelPrint(1, "Setting Value")
                valueChoice = _ConsoleHelper.LevelInput(1, "-")
                SettingsManager.Settings[keyChoice] = valueChoice
            else:
                IntChoice = _sw.Utility.StringToInteger(choice, min=dictlist_start, lessThan=dictlist_count)
                if IntChoice == None:
                    continue
                else:
                    key = dictlist[IntChoice - dictlist_start]
                    _ConsoleHelper.LevelPrint(2, '(Leave empty to cancel, or type "' + SettingsManager.__Command_Delete + '" to remove setting)')
                    _ConsoleHelper.LevelPrint(2, ">> " + SettingsManager.Settings[key])
                    choice = _ConsoleHelper.LevelInput(2, "Enter new value: ")
                    if choice == "":
                        continue
                    elif choice == SettingsManager.__Command_Delete:
                        del SettingsManager.Settings[key]
                    else:
                        SettingsManager.Settings[key] = choice
        return

    @staticmethod
    def Console_PrintSettingsMenu():
        while(True):
            _ConsoleHelper.ClearConsoleWindow()
            _ConsoleHelper.LevelPrint(0, "[Settings Menu]")
            _ConsoleHelper.LevelPrint(1, "1.Change settings")
            _ConsoleHelper.LevelPrint(1, "2.Reset settings")
            _ConsoleHelper.LevelPrint(1, "3.Open Settings Directory")
            _ConsoleHelper.LevelPrint(1, "0.Go back")
            _ConsoleHelper.LevelPrint(1)
            choice = input("-")
            if choice == "1":
                SettingsManager.__Console_ChangeSettings()
            elif choice == "2":
                _ConsoleHelper.LevelPrint(1, "-Confirm Reset! (y/n)")
                _ConsoleHelper.LevelPrint(1)
                choice = input("-")
                if choice == "y":
                    SettingsManager.Settings = None
                    SettingsManager.SaveSettings()
                    _ConsoleHelper.LevelPrint(1)
                    _ConsoleHelper.AnyKeyDialog("*Settings resetted!")
            elif choice == "3":
                fileInfo = _sw.File.FileInfo(SettingsManager._settingsPath)
                _os.startfile(fileInfo.tail)
            else:
                break
        return
