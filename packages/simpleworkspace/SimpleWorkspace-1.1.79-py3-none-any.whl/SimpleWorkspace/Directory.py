from __future__ import annotations
from typing import Callable as _Callable
import SimpleWorkspace as _sw
from queue import Queue as _Queue
import os as _os
import shutil as _shutil

def Create(path: str):
    _os.makedirs(path, exist_ok=True)

def ListFiles(searchDir: str, callback: _Callable[[str], None] = None, includeDirs=True, includeFilter:str=None, satisfiedCondition: _Callable[[str], bool] = None, exceptionCallback: _Callable[[Exception], None] = None, maxRecursionDepth: int=None) -> (list[str] | None):
    """
    Recursively iterate all driectories in a path.
    All encountered exceptions are ignored

    @param callback
        feeds full filepath to a callback
    @param includeFilter
        options takes a regex which searches full path of each file, if anyone matches a callback is called. Example: "/mySearchCriteria/i"
    @param satisfiedCondition
        takes a callback that returns a bool, if it returns true, no more search is performed
    @param exceptionCallback
        run callback on any raised exception
    @param maxRecursionDepth
        Specify how many levels down to list folders, level/depth 1 is basically searchDir entries
    @returns
        if no callback is given, a list of all found filepaths will be returned\n
        otherwise None
    """

    if not _os.path.exists(searchDir):
        return

    # only returned if callback was not given
    allEntries = [] if (callback is None) else None

    currentFolderDepth = 1 #this is basically the base directory depth with its entries and therefore the minimum value
    folders = _Queue()
    folders.put(searchDir)
    while folders.qsize() != 0:
        currentFolder = folders.get()
        try:
            currentFiles = _os.listdir(currentFolder)
            for filePath in currentFiles:
                filePath = _os.path.join(currentFolder, filePath)
                pathMatchesIncludeFilter = includeFilter == None or _sw.Utility.RegexMatch(includeFilter, filePath) != None
                if _os.path.isfile(filePath):
                    if pathMatchesIncludeFilter:
                        if callback != None:
                            try:
                                callback(filePath)
                            except Exception as e:
                                if(exceptionCallback != None):
                                    exceptionCallback(e)
                        else:
                            allEntries.append(filePath)
                else:
                    if includeDirs:
                        if pathMatchesIncludeFilter:
                            if callback != None:
                                try:
                                    callback(filePath)
                                except Exception as e:
                                    if(exceptionCallback != None):
                                        exceptionCallback(e)
                            else:
                                allEntries.append(filePath)
                    folders.put(filePath)
                if satisfiedCondition != None and satisfiedCondition(filePath):
                    return
            currentFolderDepth += 1
            if (maxRecursionDepth != None) and (currentFolderDepth > maxRecursionDepth):
                break
        except Exception as e:
            if(exceptionCallback != None):
                exceptionCallback(e)
    return allEntries


def Remove(path: str) -> None:
    _shutil.rmtree(path, ignore_errors=True)
