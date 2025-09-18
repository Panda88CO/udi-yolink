
try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
except ImportError:
    import logging
    logging.basicConfig(level=logging.DEBUG)

class LocalAccess (object):
    def check_local_hub(self)
    l   ogging.info('adding/checking device : {} - {}'.format(dev['name'], dev['type']))
                if dev['type'] == 'Hub':     
                    logging.info('Hub not added - ISY cannot do anything useful with it')    
                    if  model in ['YS1606',]:
                        self.local_access = True
                        self.yoAccess.initializeLocalAccess(self.client_id, self.client_secret, self.local_ip)
                        self.poly.Notices['local_access'] = 'Local Hub detected - Enabling local access'