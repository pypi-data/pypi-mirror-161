import requests




class Config(object):
    def __init__(self, config_name, debug_request=False):
        self.config_name = config_name
        self.debug_request = debug_request
        self._config = None

    def _getConfig(self):
        res = requests.get(f"https://config.openscreen.com/{self.config_name}.json", timeout=25000)
        if res.status_code == 200:
            data = res.json()
            self._config = data
            res.close()
            return
        else:
            res.close()
            raise Exception(f"Openscreen: unable to load cloud configuration {self.config_name}")

    @property
    def config(self):
        return self._config

    def loadConfig(self):
        self._getConfig()

