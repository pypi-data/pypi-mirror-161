from __future__ import annotations as _annotations
from abc import ABC, abstractmethod
from SimpleWorkspace import ConsoleHelper as _ConsoleHelper
import os as _os
import json as _json
import SimpleWorkspace as _sw

class SettingsManager_Base(ABC):
    _settingsPath = None
    settings = {}

    def __init__(self, settingsPath):
        self._settingsPath = settingsPath
        self.settings = self._GetDefaultSettings()

    def _GetDefaultSettings(self):
        return {}

    @abstractmethod
    def _ParseSettingsFile(filepath):
        pass
    @abstractmethod
    def _ExportSettingsFile(settingsObject, outputPath):
        pass

    def ClearSettings(self):
        self.settings = self._GetDefaultSettings()

    def LoadSettings(self):
        self.ClearSettings()
        if not (_os.path.exists(self._settingsPath)):
            return
        if _os.path.getsize(self._settingsPath) == 0:
            return
        try:
            self._ParseSettingsFile(self._settingsPath)
        except Exception as e:
            _os.rename(self._settingsPath, self._settingsPath + ".bak")
        return self.settings

    def SaveSettings(self):
        self._ExportSettingsFile(self.settings, self._settingsPath)


class SettingsManager_JSON(SettingsManager_Base):
    def _ParseSettingsFile(self, filepath):
        self.settings = _json.loads(_sw.File.Read(filepath))
        return

    def _ExportSettingsFile(self, settingsObject, outputPath):
        jsonData = _json.dumps(settingsObject)
        _sw.File.Create(outputPath, jsonData)
        return



class SettingsManager_InteractiveConsole(SettingsManager_JSON):
    __Command_Delete = "#delete"

    def __Console_ChangeSettings(self):
        while True:
            _ConsoleHelper.ClearConsoleWindow()
            _ConsoleHelper.LevelPrint(0, "[Change Settings]")
            _ConsoleHelper.LevelPrint(1, "0. Save Settings and go back.(Type cancel to discard changes)")
            _ConsoleHelper.LevelPrint(1, "1. Add a new setting")
            _ConsoleHelper.LevelPrint(2, "[Current Settings]")
            dictlist = []
            dictlist_start = 2
            dictlist_count = 2
            for key in self.settings:
                _ConsoleHelper.LevelPrint(3, str(dictlist_count) + ". " + key + " : " + str(self.settings[key]))
                dictlist.append(key)
                dictlist_count += 1
            _ConsoleHelper.LevelPrint(1)
            choice = input("-Choice: ")
            if choice == "cancel":
                self.LoadSettings()
                _ConsoleHelper.AnyKeyDialog("Discarded changes!")
                break
            if choice == "0":
                self.SaveSettings()
                _ConsoleHelper.LevelPrint(1)
                _ConsoleHelper.AnyKeyDialog("Saved Settings!")
                break
            elif choice == "1":
                _ConsoleHelper.LevelPrint(1, "Setting Name:")
                keyChoice = _ConsoleHelper.LevelInput(1, "-")
                _ConsoleHelper.LevelPrint(1, "Setting Value")
                valueChoice = _ConsoleHelper.LevelInput(1, "-")
                self.settings[keyChoice] = valueChoice
            else:
                IntChoice = _sw.Utility.StringToInteger(choice, min=dictlist_start, lessThan=dictlist_count)
                if IntChoice == None:
                    continue
                else:
                    key = dictlist[IntChoice - dictlist_start]
                    _ConsoleHelper.LevelPrint(2, '(Leave empty to cancel, or type "' + self.__Command_Delete + '" to remove setting)')
                    _ConsoleHelper.LevelPrint(2, ">> " + str(self.settings[key]))
                    choice = _ConsoleHelper.LevelInput(2, "Enter new value: ")
                    if choice == "":
                        continue
                    elif choice == self.__Command_Delete:
                        del self.settings[key]
                    else:
                        self.settings[key] = choice
        return

    def Console_PrintSettingsMenu(self):
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
                self.__Console_ChangeSettings()
            elif choice == "2":
                _ConsoleHelper.LevelPrint(1, "-Confirm Reset! (y/n)")
                choice = _ConsoleHelper.LevelInput(1, "-")
                if choice == "y":
                    self.ClearSettings()
                    self.SaveSettings()
                    _ConsoleHelper.LevelPrint(1)
                    _ConsoleHelper.AnyKeyDialog("*Settings resetted!")
            elif choice == "3":
                fileInfo = _sw.File.FileInfo(self._settingsPath)
                _os.startfile(fileInfo.tail)
            else:
                break
        return
 