import gzip as _gzip
import logging as _logging
from logging.handlers import RotatingFileHandler as _RotatingFileHandler
import time as _time
import os as _os
from SimpleWorkspace import Conversion as _Conversion

class FileLogger:
    @staticmethod
    def GetLogger(filepath, minimumLogLevel=_logging.DEBUG, maxBytes=_Conversion.Bytes.MB * 100, maxRotations=10):
        def rotator(source, dest):
            with open(source, "rb") as sf:
                gzip_fp = _gzip.open(dest, "wb")
                gzip_fp.writelines(sf)
                gzip_fp.close()
            _os.remove(source)



        logger = _logging.getLogger("__FILELOGGER_" + str(hash(filepath)))
        logger.setLevel(minimumLogLevel)
        handler = _RotatingFileHandler(filepath, maxBytes=maxBytes, backupCount=maxRotations)
        handler.rotator = rotator
        handler.namer = lambda name: name + ".gz"
        formatter = _logging.Formatter(
            fmt='%(asctime)s.%(msecs)04d+00:00 - %(levelname)s - <%(module)s, %(lineno)s> %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
            
        formatter.converter = _time.gmtime
            
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
class DummyLogger:
    @staticmethod
    def GetLogger():
        dummyLogger = _logging.getLogger('@@BLACKHOLE@@')
        dummyLogger.addHandler(_logging.NullHandler())
        dummyLogger.propagate = False
        return dummyLogger