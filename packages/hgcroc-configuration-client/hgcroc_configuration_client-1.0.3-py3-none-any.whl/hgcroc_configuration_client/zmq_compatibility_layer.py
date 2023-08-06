import yaml
import logging
from client import Client
from hgcal_utilities import hgcal_utilities


class i2cController:
    """
    Compatibility layer between the hgcroc-tools i2c client interface and
    scripts expecting the zmqController and i2cController client interface.
    """

    def __init__(self, ip, port, fname=None):
        """
        Initialize the client and class variables, and get description
        from the hexaboard

        Parameters
        ----------
        ip
            Address or hostname of the board to connect to
        port
            Port of the board expecting the connection
        fname
            Initial configuration to use unless overridden by a parameter
            supplied to a different method. Included for compatibility
        """
        self.logger = logging.getLogger("i2cController")
        self.client = Client(ip, port)
        # Get board description
        self.description = self.client.describe()

        if fname is not None:
            with open(fname, "r") as f:
                raw_config = yaml.safe_load(f)
            self.yamlConfig = self._convert(raw_config)
        else:
            self.logger.warning("No default config specified")

    def _convert(self, raw_dict):
        board_type = list(self.description.keys())[0]
        board_layout = self.description[board_type]
        rocs = board_layout.keys()
        # Trim off configuration parameters that are not part of hexaboard
        trimmed_config = {}
        for roc in rocs:
            if roc not in raw_dict.keys():
                self.logger.warning(f'ROC {roc} not in configuration. Make '
                                    f'sure configuration is for {board_type}')
            else:
                trimmed_config[roc] = raw_dict[roc]['sc']
        # Expand block entries defined by 'all' into dicts for each block,
        # then merge any specified blocks into this
        converted_dict = {}
        for roc in trimmed_config.keys():
            converted_dict[roc] = {}
            for subBlock, block_dict in trimmed_config[roc].items():
                if 'all' in block_dict.keys():
                    global_config = block_dict['all']
                    del block_dict['all']
                    blocks_with_all = {key: global_config for key in
                                       board_layout[roc][subBlock].keys()}
                    # Merge specified blocks into blocks_with_all
                    for block in block_dict.keys():
                        blocks_with_all[block] = \
                                hgcal_utilities.update_dict(
                                        blocks_with_all[block],
                                        block_dict[block])
                # Note: yaml will dump this dict with references by default
                converted_dict[roc][subBlock] = blocks_with_all

        return converted_dict

    def _chooseNotNone(self, config_file: str, config_dict: dict):
        """
        Returns whichever non-default configuration is not 'None'. If both are
        not 'None', returns the default_config. If both are not specified,
        prioritizes config_dict. This behaviour is taken from the zmqController
        """
        return_config = self.yamlConfig
        if config_file is None:
            if config_dict is not None:
                return_config = self._convert(config_dict)
        else:
            with open(config_file, "r") as f:
                raw_config = yaml.safe_load(f)
            return_config = self._convert(raw_config)

        return return_config

    def reset(self):
        self.client.reset()

    def update_yamlConfig(self, fname=None, yamlNode=None):
        """
        Merge a new configuration into the existing one

        Parameters
        ----------
        fname
            A path to a yaml file containing a configuration to be merged.
            Lower priority than yamlNode
        yamlNode
            A configuration dictionary. If fname is specified, this will be
            preferred. This behaviour is taken from the original zmqController
        """
        new_config = self._chooseNotNone(fname, yamlNode)
        if new_config == self.yamlConfig:
            self.logger.warning("No new configuration specified to update")
        else:
            self.yamlConfig = hgcal_utilities.update_dict(
                    self.yamlConfigconfig, new_config)

    def initialize(self, fname=None, yamlNode=None):
        config = self._chooseNotNone(fname, yamlNode)
        self.client.set(config)

    def configure(self, fname=None, yamlNode=None):
        config = self._chooseNotNone(fname, yamlNode)
        self.client.set(config)

    def read_config(self, yamlNode=None):
        if yamlNode is None:
            response = self.client.get()
        else:
            not_nulled = self._convert(yamlNode)
            response = self.client.get(not_nulled)

        return response

    def read_pwr(self):
        raise NotImplementedError("read_pwr not implemented")

    def resettdc(self):
        board_type = list(self.description.keys())[0]
        board_layout = self.description[board_type]
        raw_config = {roc: {'sc': {'MasterTdc': {'all': {'START_COUNTER': 0}}}}
                      for roc in board_layout.keys()}
        self.configure(yamlNode=raw_config)  # formats and sends dict
        raw_config = {roc: {'sc': {'MasterTdc': {'all': {'START_COUNTER': 1}}}}
                      for roc in board_layout.keys()}
        self.configure(yamlNode=raw_config)  # formats and sends dict

        return "masterTDCs reset."

    def measadc(self, yamlNode):
        raise NotImplementedError("measadc not implemented")

    def configure_injection(self, injectedChannels, activate=0,
                            gain=0, phase=None, calib_dac=0):
        board_type = list(self.description.keys())[0]
        board_layout = self.description[board_type]
        if gain == 0:
            LR = activate
            HR = 0
        else:
            LR = 0
            HR = activate
        config = {}
        for roc in board_layout.keys():
            if calib_dac == -1:
                config[roc] = {'ReferenceVoltage': {0: {'IntCtest': 0},
                                                    1: {'IntCtest': 0}}}
            else:
                config[roc] = {'ReferenceVoltage':
                               {0: {'IntCtest': activate},
                                1: {'IntCtest': activate}}}
                config[roc]['ReferenceVoltage'][0]['Calib'] = \
                    calib_dac
                config[roc]['ReferenceVoltage'][1]['Calib'] = \
                    calib_dac
            if phase is not None:
                config[roc]['Top'] = {0: {'phase_ck': phase}}
            config[roc]['ch'] = {}
            for channel in injectedChannels:
                config[roc]['ch'][channel] = {'LowRange': LR,
                                              'HighRange': HR}
        self.client.set(config)
        if phase is not None:
            self.resettdc()
