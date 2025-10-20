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
import time
import argparse


PHYPHOX_API = {"start": "/control?cmd=start",
               "stop": "/control?cmd=stop",
               "clear": "/control?cmd=clear",
               "meta": "/meta",
               "config": "/config",
               "time": "/time",
               }


class PhyphoxSensor():
    """
    PhyphoxSensor class
    """
    def __init__(self, metadata=None):
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
            raise TypeError("metadata is not a dict in PhyphoxSensor")

    def get(self, key):
        """
        get key in JSON sensor description
        parameter key: str
        return key value  if key exist otherwise None
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
        return 'PhyphoxSensor('+str(self.__meta)+')'


class Experiment():
    """
    Phyphox Experience class
    https://phyphox.org/wiki/index.php/Remote-interface_communication#.2Fconfig
    https://phyphox.org/wiki/index.php/Phyphox_file_format
    """
    def __init__(self, metadata=None):
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

    def get(self, key):
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


class PhyphoxLogger():
    """
    PhyphoxLogger class
    meta :
    https://phyphox.org/wiki/index.php/Remote-interface_communication#.2Fmeta
    :meta private __sensors sensor used in experiment
    :meta private __config raw data for experiment configuration
    :meta private __meta raw data for meta phyphox answer
    :ivar base_url url to access phone phyphox application
    """

    def __init__(self, adresse, port=8080, protocol='http', no_proxy=False):
        if ipaddress.ip_address(adresse):
            if isinstance(port, int):
                self.__ip_adress = adresse, str(port)
            else:
                raise ValueError("port must be an integer")
        else:
            raise ValueError("IP Address not correct")
        self.base_url = protocol + "://" + \
            self.__ip_adress[0] + ":" + self.__ip_adress[1]
        self.__req_answers = {'config': {}, 'meta': {}}
        self.__sensors = {}
        self.__experiment = None
        self.__get_names = []
        self.__fs_samp_estimated = -1
        self.__first_get = True
        self.__next_time = []
        self.__nb_measure = 0
        self.__list_tabs = []
        self.channel = []
        self.legend = []
        self.verbose = False
        self.new_data = False
        self.overflow = False
        if no_proxy:
            os.environ["no_proxy"] = self.__ip_adress[0]
        logging.info("Phone adress : %s", self.base_url)
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

    def send_url(self, api_key):
        """
        open standard phyphox url
        parameter api_key: str
        return json answers or an empty dict if there is no answer
        """
        if api_key in PHYPHOX_API:
            url = self.base_url + PHYPHOX_API[api_key]
            try:
                with urllib.request.urlopen(url) as reponse:
                    reponse = reponse.read()
                return json.loads(reponse)
            except urllib.error.HTTPError:
                pass
        warnings.warn("Unknown command or not implemented")
        return {}

    def get_meta(self, key):
        """
        get key in JSON phyphox meta data
        parameter key: str
        return key value  if key exist otherwise None
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

    def start_cmd(self):
        """
        Send start command to phyphox phone application
        """
        return self.send_url("start")

    def meta_cmd(self, force_update=False):
        """
        Get meta information from phyphox phone application
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
                warnings.warn("Unknown meta key %s", str(key))

    def config_cmd(self, force_update=False):
        """
        Get config data for selected experiment
        """
        if force_update or not self.__req_answers["config"]:
            self.__req_answers["config"] = self.send_url("config")
        logging.info("CONFIG:\n%s", str(self.__req_answers["config"]))
        self.__experiment = Experiment(self.__req_answers["config"])

    def init_sensors(self):
        """
        build sensor objects using meta answer
        """
        self.__sensors = {}
        for sensor_name in self.__req_answers["meta"]["sensors"]:
            if self.__req_answers["meta"]["sensors"][sensor_name]:
                self.__sensors[sensor_name] = \
                    PhyphoxSensor(self.__req_answers["meta"]["sensors"][sensor_name])

    def clear_cmd(self):
        """
        Stop sampling and reset buffer of phyphox phone application
        """
        self.__nb_measure = 0
        return self.send_url("clear")

    def stop_cmd(self):
        """
        Stop sampling of phyphox phone application
        """
        return self.send_url("stop")

    def time_cmd(self):
        """
        Get phone time reference
        """
        return self.send_url("time")

    def export_file(self, filetype=0, filename="data.xls"):
        """
        retrieve all recorded data in a single file
        format can be 
        0 for xls
        1 zip file included csv with comma separator and decimal point
        2 zip file included csv with tabulator separator and decimal point
        3 zip file included csv with semicolon separator and decimal point
        4 zip file included csv with tabulator separator and decimal comma
        5 zip file included csv with semicolon separator and decimal comma        
        """
        url = self.base_url + "/export?format=" + str(filetype)
        with urllib.request.urlopen(url) as reponse:
            reponse = reponse.read()
        # self.__config = json.loads(reponse)
        logging.info("CONFIG:\n%s", str(reponse))
        with open(filename,"wb") as fd:
            fd.write(reponse)
        

    def buffer_needed(self, l_exp=None):
        """
        Select buffer in phyphox config
        if parameter is None all buffer are selected
        otherwise l_exp is list of tuple (id, b_id1, ...) where
        id is source index in config data and
        b_idx is buffer index in source list.
        """
        exp = self.__experiment
        if l_exp:
            for idx_exp, *idx_buf in l_exp:
                names = []
                key_sensor = exp.source_names[idx_exp].lower()
                if key_sensor in self.__sensors:
                    freq = self.__sensors[key_sensor]['MinDelay']
                    freq = 1 / float(freq) * 1e6
                    if self.__fs_samp_estimated < 0:
                        self.__fs_samp_estimated = freq
                    elif freq < self.__fs_samp_estimated:
                        self.__fs_samp_estimated = freq
                if 0 <= idx_exp < len(exp.buffer_names):
                    for idx in idx_buf:
                        if idx < 0 or idx >= len(exp.buffer_names[idx_exp]):
                            raise IndexError("there is only ",
                                             len(exp.buffer_names[idx_exp]),
                                             ", buffer in this experiment")
                        names.append(exp.buffer_names[idx_exp][idx])
                    self.__get_names.append(names)
                else:
                    raise IndexError("there is only ",
                                     len(exp.buffer_names),
                                     ", experiment")
        else:
            self.__get_names = copy.deepcopy(exp.buffer_names)
        return True

    def build_link(self, val_time=None):
        """
        Create link to retrieve buffer selected
        In first call full data are retrieve otherwise last time
        buffer value is used to get only new data
        """
        base = ""
        if self.__first_get or val_time is None:
            self.__nb_measure = 0
            for l_name in self.__get_names:
                for name in l_name:
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

    def get_measure(self, stack_data=True, full_data=False):
        """
        get data for selected buffer and put data
        in a list of numpy array (private attribute __numpy_tabs)
        if stack_data is True data are pushed in a list otherwise
        only last data are keep in memory
        """
        if not full_data:
            lnk = self.build_link(self.__next_time)
        else:
            lnk = self.build_link(val_time=None)
        logging.info(self.base_url + lnk)
        with urllib.request.urlopen(self.base_url + lnk) as reponse:
            reponse = reponse.read()
            logging.info("LNK answer:\n%s", str(reponse))
            data = json.loads(reponse)
        if len(data['buffer'][self.__get_names[0][0]]['buffer']) == 0:
            self.new_data = False
            return
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

    def get_nb_measure(self):
        """
        return number of measure for first buffer
        """
        return self.__nb_measure

    def get_last_measure(self):
        """
        return last buffer array
        """
        return self.__list_tabs[-1]

    def print_buffer_name(self):
        """
        Print available buffer in config data
        """
        if not self.__req_answers["config"]:
            self.config_cmd()
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


