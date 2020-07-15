import time
import sys
import os
try:
    from .server import Server_Control
    from .fespc import FrontEndServerProcessControl
except ImportError:
    try:
        from utils.server import Server_Control
        from utils.fespc import FrontEndServerProcessControl
    except ImportError:
        try:
            from .utils.server import Server_Control
            from .utils.fespc import FrontEndServerProcessControl
        except ImportError:
            try:
                from server import Server_Control
                from fespc import FrontEndServerProcessControl
            except ImportError:
                class Check_Update:
                    def __init__(self, SC):
                        self.server_control = SC
                        self.server = SC.server
                        self.Mlogger = self.server_control.Mlogger

                    def get_version(self):
                        pass

                    def check_update(self):
                        pass

                    def restart_all(self, ttw: int):
                        self.server.restart_program(ttw)


try:
    sbtmp = Check_Update
except NameError:
    class Check_Update:
        def __init__(self, SC: Server_Control):
            self.server_control = SC
            self.server: FrontEndServerProcessControl = SC.server
            self.Mlogger = self.server_control.Mlogger

        def get_version(self):
            pass

        def check_update(self):
            pass

        def restart_all(self, ttw: int):
            self.server.restart_program(ttw)
