


import os
from logging.handlers import RotatingFileHandler


class ExMyBFileHandler(RotatingFileHandler):

    def doRollover(self):
        """
        Override base class method to make the new log file group writable.
        """
        # Rotate the file first.
        RotatingFileHandler.doRollover(self)

        # Add group write to the current permissions.
        stat_info = os.stat(self.baseFilename)
        currMode = stat_info.st_mode
        uid = stat_info.st_uid
        gid = stat_info.st_gid
        os.chmod(self.baseFilename, currMode)
        os.chown(self.baseFilename, uid, gid)
