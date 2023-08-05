import logging
import os
import datetime

class ProjectLogger:
    
    def __init__(
                  self,
                  logfile=None,
                  mode='a',
                  modules={'resumableds':logging.DEBUG, '': logging.INFO},
                ):
        
        self.logfile = logfile
        
        if self.logfile:
            # config logfile
            handler = logging.FileHandler(self.logfile, mode=mode)
        else:
            # log to stdout
            handler = logging.StreamHandler()
            '''
            date = datetime.date.today().strftime('%Y%m%d')
            logloc = os.getcwd()
            # move up if we are in the notebooks or src dir (assuming ds cookiecutter dir structure)
            if os.path.basename(logloc) in ('src', 'notebooks'):
                logloc = os.path.dirname(logloc)
            self.logfile = os.path.join(logloc, '{}.log'.format(date))
            '''
        
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(name)s.%(funcName)s/%(lineno)d] %(message)s')
        handler.setFormatter(formatter)    
        
        # define module log levels
        for module, loglevel in modules.items():
            logging.getLogger(module).setLevel(loglevel)
            
        # add logfile handler to root logger
        logging.getLogger('').addHandler(handler)
