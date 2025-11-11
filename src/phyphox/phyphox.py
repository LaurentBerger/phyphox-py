"""
PhyphoxLogger class
to connect your phone to your python application
"""
import os
import urllib.request
import urllib.parse
import json
import ipaddress
import copy
import warnings
import logging
import enum


class BufferMode(enum.Enum):
    """
    Constant used to build URLs to retrieve data.
    """
    #: FULL Retrieve all data.
    FULL = 0
    #: LAST Retrieve only the last measurement (one per buffer).
    LAST = 1
    #: UPDATE Retrieve all data since the last call.
    UPDATE = 2


PHYPHOX_API = {"start": "/control?cmd=start",
               "stop": "/control?cmd=stop",
               "clear": "/control?cmd=clear",
               "meta": "/meta",
               "config": "/config",
               "time": "/time",
               }


class Sensor():
    """
    Phyphox Sensor class

    :param dict metadata: sensor metadata

    `Refer to the Phyphox documentation for details.`_ .

    .. _Refer to the Phyphox documentation for details.: https://phyphox.org/wiki/index.php/Network_Connections#Metadata
    """
    def __init__(self, metadata: dict = None):
        self.__meta = {
            'Name': None,
            'Vendor': None,
            'Range': -1,
            'Resolution': -1,
            'MinDelay': -1,
            'MaxDelay': -1,
            'Power': -1,
            'Version': None
        }
        if isinstance(metadata, dict):
            for key in metadata:
                if key in self.__meta:
                    self.__meta[key] = metadata[key]
        else:
            raise TypeError("metadata is not a dict in Phyphox Sensor")

    def get(self, key: (int, str)):
        """
        extract key in JSON sensor description

        :param str, int key: key to extract
        :return key: value if key exist otherwise None
        """
        if key in self.__meta:
            return self.__meta[key]
        return None

    def __str__(self):
        result = ""
        for key_val in self.__meta.items():
            if isinstance(key_val[1], str) and len(key_val[1]) > 100:
                result = result + key_val[0] + " : " +\
                    str(key_val[1][:100]) + " ... \n"
            else:
                result = result + key_val[0] + " : " + str(key_val[1]) + "\n"
        return result

    def __repr__(self):
        return 'Sensor('+str(self.__meta)+')'


class Experiment():
    """
    Experiment class

    :param dict metadata: experiment metadata

    `Refer to the Phyphox experiment documentation.`_ .

    .. _Refer to the Phyphox experiment documentation.: https://phyphox.org/wiki/index.php?title=Remote-interface_communication#.2Fconfig
    """
    def __init__(self, metadata: dict = None):
        self.__meta = {
            'crc32': None,
            'title': None,
            'localTitle': None,
            'category': None,
            'localCategory': None,
            'buffers': [],
            'inputs': [],
            'export': []
        }
        self.buffer_names = []
        self.source_names = []
        self.legends = []
        if isinstance(metadata, dict):
            for key in metadata:
                if key in self.__meta:
                    self.__meta[key] = metadata[key]
            self.get_experiments_struct()
        else:
            raise TypeError("metadata is not a dict in Experiment")

    def __str__(self):
        result = ""
        for key_val in self.__meta.items():
            if len(key_val[1]) > 100:
                result = result + key_val[0] + " : " +\
                    str(key_val[1][:100]) + " ... \n"
            else:
                result = result + key_val[0] + " : " + str(key_val[1]) + "\n"
        return result

    def __repr__(self):
        return 'Experiment('+str(self.__meta)+')'

    def get(self, key: (int, str)):
        """
        get key in JSON phyphox config data
        parameter key: str
        return key value  if key exist otherwise None
        """
        if key in self.__meta:
            return self.__meta[key]
        return None

    def get_experiments_struct(self):
        """
        Get information about experiment from phyphox phone application
        """
        for cpt_set in self.__meta['export']:
            canaux_exp = []
            legend_exp = []
            self.source_names.append(cpt_set['set'])
            for src in cpt_set['sources']:
                canaux_exp.append(src['buffer'])
                legend_exp.append(src["label"])
            if len(canaux_exp) > 0:
                self.legends.append(legend_exp)
                self.buffer_names.append(canaux_exp)


class Logger():
    """
    Phyphox Logger class

    :param str ip: Device IP address.
    :param int port: Port number (default: 8080).
    :param str protocol: Communication protocol (default: 'http').
    :param bool no_proxy: If True, disables proxy usage by setting the environment variable (default: False).
    :meta private config: raw data for experiment configuration
    :meta private meta: raw data for meta phyphox answer
    """

    def __init__(self, adresse, port=8080, protocol='http', no_proxy=False):
        """The constructor

        :ivar base_url: URL to access the Phyphox application on the phone.
        :param str adresse: mobile phone address
        :param int port: port number (default: 8080).
        :param str protocol: default is http
        :param bool no_proxy: default False. True try disable proxy using environment variable
        """
        if ipaddress.ip_address(adresse):
            if isinstance(port, int):
                self.__ip_adress = adresse, str(port)
            else:
                raise ValueError("port must be an integer")
        else:
            raise ValueError("IP Address not correct")
        #: url to access phone phyphox application
        self.base_url = protocol + "://" + \
            self.__ip_adress[0] + ":" + self.__ip_adress[1]
        self.__req_answers = {'config': {}, 'meta': {}}
        #: sensors: sensor used in experiment
        self.__sensors = {}
        self.__experiment = None
        self.__get_names = []
        self.__first_get = True
        self.__next_time = []
        self.__nb_measure = 0
        self.__list_tabs = []
        self.__cmd_response = None
        #: channel  name
        self.channel = []
        #: legend for each channel
        self.legend = []
        #: True when new data is available
        self.new_data = False
        #: True when new data overflow non read data
        self.overflow = False
        if no_proxy:
            os.environ["no_proxy"] = self.__ip_adress[0]
        logging.info("Phone adress : %s", self.base_url)
        #: know key see
        self.__metakeys = {
            'version': None,
            'build': None,
            'fileFormat': None,
            'deviceModel': None,
            'deviceBrand': None,
            'deviceBoard': None,
            'deviceManufacturer': None,
            'deviceBaseOS': None,
            'deviceCodename': None,
            'deviceRelease': None,
            'depthFrontSensor': None,
            'depthBackSensor': None,
            'depthFrontRate': None,
            'depthBackRate': None,
            'depthFrontResolution': None,
            'depthBackResolution': None,
            'camera2api': None,
            'camera2apiFull': None}

    def __str__(self):
        result = ""
        for key_val in self.__metakeys.items():
            if key_val[0] != 'sensors':
                if key_val[1] and len(key_val[1]) > 100:
                    result = result + key_val[0] + " : " +\
                        str(key_val[1][:100]) + " ... \n"
                elif key_val[1]:
                    result = result + key_val[0] + " : " +\
                        str(key_val[1]) + "\n"
        if self.__experiment:
            print(self.__experiment)
        for sensor in self.__sensors.items():
            print(sensor[0], "\t", sensor[1])
        return result

    def send_url(self, cmd_key):
        """
        open standard phyphox URL.

        :param str cmd_key: Command to send
        :return dict: A dictionary with the JSON response, or an empty dict if no response.
        """
        if cmd_key in PHYPHOX_API:
            url = self.base_url + PHYPHOX_API[cmd_key]
            try:
                with urllib.request.urlopen(url) as reponse:
                    self.__cmd_response = reponse.read()
                return json.loads(self.__cmd_response)
            except urllib.error.HTTPError:
                pass
        warnings.warn("Unknown command or not implemented")
        return {}

    def get_meta_key(self, key):
        """
        Retrieves a key from the JSON metadata.

        :param str key: Key to retrieve.
        :return: Key value if it exists, otherwise None.
        """
        if key in self.__req_answers["meta"]:
            return self.__req_answers["meta"][key]
        return None

    def print_reponse(self, json_reponse, niveau=0):
        """
        Affichage des données json de la structure
        """
        for cle in json_reponse.keys():
            if isinstance(json_reponse[cle], dict):
                print(niveau * '\t' + cle)
                self.print_reponse(json_reponse[cle], niveau + 1)
            elif isinstance(json_reponse[cle], list):
                print(niveau * '\t' + cle)
                for elt_json in json_reponse[cle]:
                    self.print_reponse(elt_json, niveau + 1)
            else:
                print(niveau * '\t' + cle, ":", json_reponse[cle])

    def start(self):
        """
        Sends the start command to the Phyphox app.

        :return: JSON response (True on success).
        """
        return self.send_url("start")

    def get_meta(self, force_update=False):
        """
        Get meta information from phyphox phone application

        :param bool force_update: True retrieve data from mobile phone otherwise use old data.
        """
        if force_update or not self.__req_answers["meta"]:
            self.__req_answers["meta"] = self.send_url("meta")
        logging.info("META\n%s", str(self.__req_answers["meta"]))
        for key in self.__req_answers["meta"]:
            if key in self.__metakeys:
                self.__metakeys[key] = self.__req_answers["meta"][key]
            elif key == 'sensors':
                self.init_sensors()
            else:
                warnings.warn("Unknown meta key " + str(key))

    def get_config(self, force_update=False):
        """
        Retrieves configuration data for the selected experiment.
        """
        if force_update or not self.__req_answers["config"]:
            self.__req_answers["config"] = self.send_url("config")
        logging.info("CONFIG:\n%s", str(self.__req_answers["config"]))
        self.__experiment = Experiment(self.__req_answers["config"])

    def init_sensors(self):
        """
        Builds sensor objects using metadata.
        """
        self.__sensors = {}
        for sensor_name in self.__req_answers["meta"]["sensors"]:
            if self.__req_answers["meta"]["sensors"][sensor_name]:
                self.__sensors[sensor_name] = \
                    Sensor(self.__req_answers["meta"]["sensors"][sensor_name])

    def clear_data(self):
        """
        Stop sampling and reset buffer in the Phyphox app.

        :return: JSON response (True on success).
        """
        self.__nb_measure = 0
        return self.send_url("clear")

    def stop(self):
        """
        Stop sampling of phyphox phone application

        :return: JSON response (True on success).
        """
        return self.send_url("stop")

    def get_time(self):
        """
        Get phone time reference
        """
        return self.send_url("time")

    def export_file(self, filetype=0, filename="data.xls"):
        """
        Retrieves all recorded data in a single file.
        File types:
        0 for xls
        1 zip file included csv with comma separator and decimal point
        2 zip file included csv with tabulator separator and decimal point
        3 zip file included csv with semicolon separator and decimal point
        4 zip file included csv with tabulator separator and decimal comma
        5 zip file included csv with semicolon separator and decimal comma

        :param int filetype: default is 0 for xls
        :param str filename: file name to save. default is "data.xls"
        """
        url = self.base_url + "/export?format=" + str(filetype)
        with urllib.request.urlopen(url) as reponse:
            reponse = reponse.read()
        # self.__config = json.loads(reponse)
        logging.info("CONFIG:\n%s", str(reponse))
        with open(filename, "wb") as fd:
            fd.write(reponse)

    def buffer_needed(self, l_exp=None):
        """
        Selects buffers in the Phyphox configuration.
        if l_exp is None, all buffers are selected.
        Otherwise, l_exp must be a list of tuples (id, (b_id1, …)),
        where id is the source index in the configuration data,
        and b_id is the buffer index in the source list.

        :param list l_exp: list of tuple. default value is None
        :return bool: False is something wrong in list
        """
        if not self.__req_answers["config"]:
            self.get_config()
        exp = self.__experiment
        self.__get_names = []
        if not l_exp:
            self.__get_names = copy.deepcopy(exp.buffer_names)
            return True
        for idx_exp, idx_buf in l_exp:
            names = []
            if idx_exp < 0 or idx_exp >= len(exp.source_names):
                warnings.warn("There is no " + str(idx_exp) +
                              " experience in configuration." +
                              " Check your selected buffer.")
                return False
            for idx in idx_buf:
                if idx < 0 or idx >= len(exp.buffer_names[idx_exp]):
                    warnings.warn("there is only " +
                                  str(len(exp.buffer_names[idx_exp])) +
                                  ", buffer in this experiment")
                else:
                    names.append(exp.buffer_names[idx_exp][idx])
            self.__get_names.append(names)
        return True

    def get_buffer_name(self, idx: int) -> str:
        """
        Returns the name of the buffer at index idx.

        :return str: buffer name
        """
        if 0 <= idx[0] < len(self.__get_names):
            if 0 <= idx[1] < len(self.__get_names[idx[0]]):
                return self.__get_names[idx[0]][idx[1]]
        return ''

    def build_link(self, val_time=None, only_last=False):
        """
        Creates a link to retrieve selected buffers.
        On the first call, all data are retrieved;
        on subsequent calls, only data after val_time are retrieved.

        :param (float, int) val_time:
        :param bool only_last:
        """
        if not self.__get_names:
            warnings.warn("No buffer selected. Call buffer_needed first")
            return ""
        base = ""
        if self.__first_get or val_time is None or only_last:
            self.__nb_measure = 0
            for l_name in self.__get_names:
                for name in l_name:
                    if only_last:
                        base = base + name + "&"
                    else:
                        base = base + name + "=full&"
            base = "/get?" + base[:-1]
        else:
            if len(val_time) != len(self.__get_names):
                logging.info("bug %d %d", val_time, len(self.__get_names))
                val_time = len(self.__get_names) * [val_time[0]]
                warnings.warn("build_link time threshold duplicated")
            for l_name, tps in zip(self.__get_names, val_time):
                for idx, name in enumerate(l_name):
                    if idx == 0:
                        base = base + name + '=' + str(tps) + '&'
                        tps_var = name
                    else:
                        base = base + name + '=' +\
                            str(tps) + '%7C' + tps_var + '&'
            base = "/get?" + base[:-1]
        return base

    def read_buffers(self, stack_data=True, mode_data=BufferMode.UPDATE):
        """
        read data for selected buffer and put data
        in a list of numpy array (private attribute __numpy_tabs)
        if full data is True all data since experiment begining is
        retrieve otherwise only data since last call.
        if stack_data is True data are pushed in a list otherwise
        only last data are keep in memory

        :param bool stack_data: True data are pushed in a list otherwise only last data are keep in memory

        :param BufferMode mode_data: see
        :return: True if new data are available
        """

        match mode_data:
            case BufferMode.FULL:
                lnk = self.build_link(val_time=None)
            case BufferMode.UPDATE:
                lnk = self.build_link(self.__next_time)
            case BufferMode.LAST:
                lnk = self.build_link(only_last=True)
            case _:
                lnk = ""
        if not lnk:
            warnings.warn("No buffer selected or invali mode_data." +
                          "Cannot get data")
            self.new_data = False
            return self.new_data
        logging.info(self.base_url + lnk)
        with urllib.request.urlopen(self.base_url + lnk) as reponse:
            reponse = reponse.read()
            logging.info("LNK answer:\n%s", str(reponse))
            data = json.loads(reponse)
        if len(data['buffer'][self.__get_names[0][0]]['buffer']) == 0:
            self.new_data = False
            return self.new_data
        self.__next_time = []
        self.__first_get = False
        self.__nb_measure = self.__nb_measure +\
            len(data['buffer'][self.__get_names[0][0]]['buffer'])
        list_tabs = []
        for l_ in self.__get_names:
            data_exp = []
            data_exp.append(data['buffer'][l_[0]]['buffer'])
            self.__next_time.append(data['buffer'][l_[0]]['buffer'][-1])
            for name in l_[1:]:
                data_exp.append(data['buffer'][name]['buffer'])
            list_tabs.append(data_exp)
        if stack_data:
            self.__list_tabs.append(list_tabs)
        else:
            if self.new_data:
                self.overflow = True
            else:
                self.overflow = False
            self.__list_tabs = [list_tabs]
        self.new_data = True
        return self.new_data

    def get_nb_measure(self):
        """
        Returns the number of measurements for the first buffer.
        """
        return self.__nb_measure

    def get_last_buffer_read(self):
        """
        Returns the last buffer list.
        """
        if self.new_data:
            return self.__list_tabs[-1]
        return []

    def get_all_buffer_read(self):
        """
        Returns a deep copy of all read buffers.
        """
        if self.new_data:
            return copy.deepcopy(self.__list_tabs)
        return []

    def print_buffer_name(self):
        """
        Prints available buffers from configuration data.
        """
        if not self.__req_answers["config"]:
            self.get_config()
        if not self.__req_answers["config"]:
            warnings.warn("Cannot get config data")
            return
        exp = self.__experiment
        print(exp.get('title'))
        for src, l_names, l_legends in zip(exp.source_names,
                                           exp.buffer_names,
                                           exp.legends):
            print("Source ", src)
            for na, le in zip(l_names, l_legends):
                print("\t", na, " -> ", le)

    def print_select_buffer(self):
        """
        Print user selected buffer in config data
        """
        if not self.__get_names:
            print("No buffer selected")
            return
        for l_ in self.__get_names:
            for name in l_:
                print("Buffer ", name)
