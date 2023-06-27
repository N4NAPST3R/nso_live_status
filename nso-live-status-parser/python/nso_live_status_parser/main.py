import ncs
from ncs.application import Service
from ncs.dp import Action
from nso_live_status import run_live_status
import logging
import json
import datetime
import traceback
from check_nso_live_status import NSOLiveStatusParser

# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        vars = ncs.template.Variables()
        vars.add('DUMMY', '127.0.0.1')
        template = ncs.template.Template(service)
        template.apply('nso-live-status-parser-template', vars)


    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service postmod(service=', kp, ')')


class ExecuteLiveStatusAction(Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        self.log.info('********************************************')
        self.log.info('**********ExecuteLiveStatusAction*********')
        self.log.info('********************************************')
        start_time = datetime.datetime.now()
        try:
            with ncs.maapi.Maapi() as mapi:
                with ncs.maapi.Session(mapi, 'admin', 'system'):
                    with mapi.start_read_trans() as mapiTransaction:
                        root = ncs.maagic.get_root(mapiTransaction)
                        device_name = str(input.device)
                        self.log.info('device_name :'+device_name)
                        input_command = str(input.command)
                        self.log.info('input_command :'+input_command)
                        live_status_obj=NSOLiveStatusParser()
                        run_live_status_result= live_status_obj.get_nso_live_status_result(root, device_name, input_command)
                        logging.info('HAVING STRUCTURED O/P :'+str(run_live_status_result.has_structured_output))
                        logging.info('TYPE OF STRUCTURED O/P :'+str(type(run_live_status_result.structured_output)))
                        if run_live_status_result.has_structured_output == True:
                            run_live_status_result_json = json.dumps(run_live_status_result.structured_output, indent = 4) 
                            logging.info('STRUCTURED O/P IN JSON FORMATE :'+str(run_live_status_result_json))
                            
                            if "show inventory" == input_command and run_live_status_result.structured_output !='' and run_live_status_result.has_structured_output:
                                structured_output = run_live_status_result.structured_output['module_name']
                                for interface in structured_output :
                                    logging.info('interface :'+str(interface))
                                    pid = structured_output[interface]['pid']
                                    logging.info('PID :'+str(pid))
                                    vid = structured_output[interface]['vid']
                                    logging.info('VID :'+str(vid))
                                    sn =  structured_output[interface]['sn']
                                    logging.info('SN :'+str(sn))
                                    logging.info('===========================')

                            output.message=str(run_live_status_result_json)
                            output.success=True
                        else:
                            out_msg="Command [ "+input_command+" ] not supported at pyATS"
                            self.log.error(out_msg)
                            self.log.error(str(run_live_status_result))
                            output.message= out_msg
                            output.success=False             
        except Exception as _e:
            self.log.debug(f"{_e}")
            self.log.error(traceback.format_exc())
            output.success = False
            output.message = f'Error : {str(_e)}'

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        #self.register_service('nso-live-status-parser-servicepoint', ServiceCallbacks)
        
        self.register_action('execute-live-status-action', ExecuteLiveStatusAction)
        # Is being used internally nso to save the post check report

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
