import zmq
import yaml
import logging
from schema import Schema, Or, Optional, SchemaError


cmd_schema_send = Schema({'type':
                          Or('set', 'get', 'describe', 'reset', 'stop'),
                          Optional('read_back', default=False): bool,
                          'status': 'send',
                          'args': dict})

cmd_schema_recv = Schema({'type':
                          Or('set', 'get', 'describe', 'reset', 'stop'),
                          'status': Or('success', 'error'),
                          'args': dict,
                          Optional('errmsg'): str})


class Client():
    """
    An interface to communicate with the Hexaboard via
    hexacontroller_sc_server.
    """

    def __init__(self, ip, port="5555") -> None:
        self.logger = logging.getLogger("client")
        self.logger.info(f'Connecting to server at {ip} on port {port}')
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f'tcp://{ip}:{port}')
        self.description = None

    @staticmethod
    def set_values_for_read(config: dict) -> dict:
        """
        Utility for setting all parameters in a configuration dictionary
        to None. Used to convert a configuration dictionary into a dictionary
        which specifies which parameters to read.

        :param config: A configuration to be used to get data from ROCs
        :type config: dict
        :return: The input configuration with all parameters set to null.
            Ready to be serialized then sent
        :rtype: dict
        """
        null_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                if 'min' not in value.keys():
                    null_config[key] = \
                            Client.set_values_for_read(value)
                else:
                    null_config[key] = None
            else:
                null_config[key] = None

        return null_config

    def set(self, config: dict = None, readback: bool = False):
        """
        Takes a configuration and writes it to ROC registers

        :param config: A configuration with parameters to set
        :type config: dict
        :param readback: Flag to specify to check if write to registers was
            successful, defaults to False.
        :type readback: bool, optional
        """
        if config is None:
            self.logger.error("Provide a configuration dictionary to set")
            raise ValueError("No configuration provided to set")
        elif len(list(config.keys())) == 0:
            self.logger.error("Configuration dictionary empty")
            raise ValueError("Configuration dictionary empty")
        message = self._serialize('set', config, readback)
        self._execute_transaction(message)

    def get(self, config: dict = None) -> dict:
        """
        Takes any configuration dictionary and requests the ROC configuration
        parameters specified. If not provided, returns all parameters.

        :param config: Configuration dictionary with parameters to get
        :type config: dict, optional
        :return: Dictionary containing ROC register values as read from cache
        :rtype: dict
        """
        if config is None:
            if self.description is None:
                self.description = \
                        self._execute_transaction({'type': 'describe',
                                                   'status': 'send',
                                                   'args': {}})
            board_type = list(self.description.keys())[0]
            config = self.description[board_type]
        null_config = self.set_values_for_read(config)
        message = self._serialize('get', null_config, False)
        roc_data = self._execute_transaction(message)

        return roc_data

    def describe(self):
        """
        Returns a description of the board with parameter min and max values
        """
        if self.description is None:
            self.description = self._execute_transaction({'type': 'describe',
                                                          'status': 'send',
                                                          'args': {}})

        return self.description

    def reset(self):
        """
        Resets The ROC ASICs of the Hexaboard and sets the cache to
        default values.
        """
        message = self._serialize('reset', {}, False)
        self._execute_transaction(message)

    def stop(self):
        """
        Stop the i2c server
        """
        message = self._serialize('stop', {}, False)
        self._execute_transaction(message)

    def _execute_transaction(self, send_message: dict) -> dict:
        """
        Send a message to the server. This message must be formatted as a dict
        with the structure specified by cmd_schema_send (line 7).
        self.serialize provides a properly formatted dictionary.

        :param send_message: A dict with values for 'type', 'status', 'args'
            specified
        :type send_message: dict
        :return: An empty dict for 'type' = 'set', else a dict containing the
            readout from hexaboard
        :rtype: dict
        """
        try:
            send_message = cmd_schema_send.validate(send_message)
        except SchemaError as err:
            self.logger.error(f'Invalid dictionary: {err.args[0]}')
            raise ValueError(f"Message validation failed: {send_message}")
        else:
            self.socket.send_string(yaml.dump(send_message))
            return_message = yaml.safe_load(self.socket.recv_string())
            if return_message['status'] == 'error':
                self.logger.error('Server responded with error: '
                                  f'{return_message["errmsg"]}', exc_info=True)
                raise ValueError("Server responded with error: "
                                 f"{return_message['errmsg']}")
            roc_data = return_message['args']
            return roc_data

    def _serialize(self, type: str,
                   config: dict,
                   readback: bool) -> dict:
        """
        Create a properly formatted dictionary from arguments.

        :param type: Type of request to be made to server. Can be: set, get,
            describe, reset, stop
        :type type: str
        :param config: The configuration to be written, or the parameters to
            be read
        :type config: dict
        readback: Enables readback after writing a configuration to a ROC. Only
            used with messages of type 'set', otherwise ignored
        :type readback: bool, optional
        :return: Message ready to send to server
        :rtype: dict
        """
        formatted_dict = {'type': type,
                          'status': 'send',
                          'read_back': readback,
                          'args': config}
        try:
            formatted_dict = cmd_schema_send.validate(formatted_dict)
        except SchemaError as e:
            self.logger.error('A parameter is invalid. Parameters: '
                              f'({type}, {type(config)}, {readback})')
            raise ValueError(str(e.args[0]))

        return formatted_dict

    def _checkErrors(self, message) -> dict:
        if message['status'] == 'error':
            self.logger.error('Server responded with error: '
                              f'{message["errmsg"]}', exc_info=True)
            raise ValueError(
                    f"Server responded with error: {message['errmsg']}")

        return
