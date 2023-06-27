import ncs
from nso_live_status import run_live_status
from ncs.dp import Action
import logging
import json

class NSOLiveStatusParser():
    logging.info('***********NSOLiveStatusParser************')
    def get_nso_live_status_result(self, root, device_name, command):
        logging.info('get_nso_live_status_result')
        run_live_status_result = run_live_status(root, device_name, command)
        logging.info('COMMAND :'+str(command))    
        return run_live_status_result