"""
  Copyright (c) 2016- 2021, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import logging
import datetime
import time
import os
import threading
import json
from enum import Enum

from wiliot.wiliot_testers.offline.offline_utils import WiliotDir
from wiliot.gateway_api.gateway import WiliotGateway, ActionType, DataType, valid_output_power_vals
from wiliot.packet_data_tools.packet_list import PacketList
from wiliot.wiliot_testers.wiliot_tester_tag_result import WiliotTesterTagResult, WiliotTesterTagResultList, \
    FailureCodes, InlayTypes


class TesterName(Enum):
    OFFLINE = 'offline'
    SAMPLE = 'sample'
    SYSTEM_TEST = 'system_test'
    TAL15K = 'tal15k'
    YIELD = 'yield'


class LoggerName(Enum):
    MAIN = 'main'
    GW = 'gw'
    RESULTS = 'results'


class WiliotTesterTagTest(object):
    """
    Wiliot Tags Tester according to configurations provided by user
    """

    def __init__(self, selected_test, test_suite=None, gw_obj=None, black_list=None,
                 stop_event_trig=None, tester_name=TesterName.OFFLINE,
                 logger_name=None, logger_result_name=None, logger_gw_name=None,
                 lock_print=None, inlay=None, verbose=True):
        """
        :param logger_name: if specified the main logger is based on a predefine logger with the specified name.
                            otherwise the logger is set by the app
        :type logger_name: str
        :param logger_result_name: if specified the results logger is based on a predefine logger with the
                                   specified name. otherwise the logger is set by the app
        :type logger_result_name: str
        :param logger_gw_name: if specified the gw logger is based on a predefine logger with the specified name.
                               otherwise the logger is set by the app
        :type logger_gw_name: str
        :param tester_name: the tester type from the TesterName list
        :type tester_name: TesterName
        :param test_suite: the test suite contains all the parameters of the test.
                           the test suite structure should be as following:
                            test_suite = {"Dual Band": {"plDelay": 100,
                                                        "rssiThresholdHW": 95,
                                                        "rssiThresholdSW": 80,
                                                        "maxTtfp": 5,
                                                        "tests": [
                                                            {"name": "first_packets_ble_band",
                                                             "rxChannel": 37,
                                                             "energizingPattern": 18,
                                                             "timeProfile": [5, 10],
                                                             "absGwTxPowerIndex": -1,
                                                             "maxTime": 5,
                                                             "delayBeforeNextTest": 0,
                                                             "stop_criteria": {"num_packets": [1, 99]},
                                                             "quality_param": {"ttfp": [0, 5]}
                                                             },
                                                            {"name": "sub1G_band",
                                                             "rxChannel": 37,
                                                             "energizingPattern": 52,
                                                             "timeProfile": [5, 10],
                                                             "absGwTxPowerIndex": -1,
                                                             "maxTime": 5,
                                                             "stop_criteria": {"num_packets": [2, 99]},
                                                             "quality_param": {}
                                                             }
                                                        ]}}
        :type test_suite: dict
        :param selected_test: the name of test from the provided test suite (e.g. 'Dual Band' from the example above)
        :type selected_test: str
        :param gw_obj: if specified the gw object is based on the predefined specified gw obj,
                      otherwise the gw obj is defined by the app
        :type gw_obj: WiliotGateway
        :param black_list: a list with all the tags that are known as a noise or already tested tag that should not
                           be part of the current test
        :type black_list: list
        :param stop_event_trig: an event from outer scope which stops the app when it is triggered (set)
        :type stop_event_trig: threading.Event
        :param lock_print: if specified the logging prints according to the specified lock
        :type lock_print: threading.Lock()
        :param inlay: the tag inlay. most relevant for decrypted packets
        :type InlayTypes
        :param verbose: if True print all debug messages as well
        :type verbose: bool
        """

        self.GwObj = gw_obj
        self.gw_ver = ''
        self.tester_name = tester_name
        self.selected_test = {}
        self.time_expired = False
        self.test_end = False
        self.first_packet_timer = None
        self.test_timer = None
        self.start_test = False

        if logger_name is None:
            wiliot_logger = WiliotTesterLog(run_name='wiliot_test')

            wiliot_dir = WiliotDir()
            log_path = os.path.join(wiliot_dir.get_common_dir(), 'logs')
            if not os.path.isdir(log_path):
                os.makedirs(log_path)
            wiliot_logger.set_logger(log_path=log_path)
            self.logger = wiliot_logger.logger
            self.logger_results = wiliot_logger.results_logger
            self.logger_gw = wiliot_logger.gw_logger

        else:
            self.logger = logging.getLogger(logger_name)
            if logger_result_name is None:
                self.logger_results = logging.getLogger(logger_name)
            else:
                self.logger_results = logging.getLogger(logger_result_name)
            if logger_gw_name is None:
                self.logger_gw = logging.getLogger(logger_name)
            else:
                self.logger_gw = logging.getLogger(logger_gw_name)

        if lock_print is None:
            self._lock_print = threading.Lock()
        else:
            self._lock_print = lock_print
        self.verbose = verbose
        # Global test params
        self.set_test_suite(selected_test, test_suite, inlay)  # Set Test suite file - tests configuration

        self.gw_init()  # Set GW Object
        self.gw_reset_and_config()  # Init values for GW Object

        if black_list is None:
            self.black_list = []
        else:
            self.black_list = black_list

        self.stop_event_trig = stop_event_trig
        self.test_results = WiliotTesterTagResultList()
        self.tag_results = None

    def check_gw_version(self):
        """
        check if gw version is supported
        :return: True if version is supported
        :rtype: bool
        """
        self.gw_ver, __ = self.GwObj.get_gw_version()
        if int(self.gw_ver.split('.')[0], 16) >= 3 and int(self.gw_ver.split('.')[1], 16) >= 5 \
                and int(self.gw_ver.split('.')[2][0], 16) >= 2:
            return True
        else:
            raise Exception('GW version should be at least 3.5.2 to support accurate timing measurement')

    def gw_init(self):
        """
        initialize gw and the data listener thread
        """
        if self.GwObj is None:
            self.GwObj = WiliotGateway(auto_connect=True, logger_name=self.logger_gw.name,
                                       lock_print=threading.Lock())
        try:
            if self.GwObj.connected:
                self.GwObj.reset_buffer()
                self.GwObj.start_continuous_listener()
                if self.check_gw_version():
                    self._printing_func('GW obj initialized')
            else:
                raise Exception('gateway was not detected, please check connection')
        except Exception as e:
            self._printing_func(e, log_level=logging.WARNING)
            raise e

    def get_gw_version(self):
        """
        get the gw firmware version
        :return: gw firmware version
        :rtype: str
        """
        return self.gw_ver

    def set_test_suite(self, selected_test, test_suite=None, inlay=None):
        """
        import the test suite
        :param selected_test: the test name from the test suites
        :type selected_test: str
        :param test_suite: if specified the dict of test suites as explain in the class init
        :type test_suite: dict
        :param inlay: the tag inlay (optional)
        :type inlay: InlayTypes
        """
        # upload test suite:
        if test_suite is None:
            tester_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], self.tester_name.value)
            tests_suites_path = os.path.join(os.path.join(tester_path, 'configs'), 'tests_suites.json')
            if os.path.isfile(tests_suites_path):
                with open(tests_suites_path) as json_file:
                    test_suite = json.load(json_file)
            else:
                self._printing_func('Test Suite input is wrong', log_level=logging.WARNING)
                raise Exception('cannot find config file tests_suites.json under tester:{}'.format(self.tester_name))

        if test_suite is None:
            msg = 'Test Suite input in wrong'
            self._printing_func(msg, log_level=logging.WARNING)
            raise Exception(msg)
        else:
            if selected_test in test_suite:
                self.selected_test = test_suite[selected_test]
                self.selected_test['inlay'] = inlay
                for i, t in enumerate(self.selected_test['tests']):
                    if 'sub1gGwTxPower' in t.keys():
                        self.selected_test['tests'][i]['sub1g_power'] = t['sub1gGwTxPower']
                    else:
                        self.selected_test['tests'][i]['sub1g_power'] = None
                    if 'absGwTxPowerIndex' in t.keys():
                        self.selected_test['tests'][i]['gw_power_dict'] = \
                            valid_output_power_vals[t['absGwTxPowerIndex']]
                    elif 'absGwTxPower' in t.keys():
                        self.selected_test['tests'][i]['gw_power_dict'] = \
                            valid_output_power_vals[[p['abs_power']
                                                     for p in valid_output_power_vals].index(t['absGwTxPower'])]
                    elif 'GwTxPower' in t.keys():
                        self.selected_test['tests'][i]['gw_power_dict'] = \
                            valid_output_power_vals[
                                [p['gw_output_power'] for p in valid_output_power_vals].index(t['GwTxPower'])]
                    else:
                        self.selected_test['tests'][i]['gw_power_dict'] = None
                        if 'sub1gGwTxPower' not in t.keys():  # both output power are not defined
                            raise Exception('invalid tx gw power')

            else:
                msg = 'the selected test: {} was not found in the tests suite'.format(selected_test)
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception(msg)

    def gw_reset_and_config(self):
        """
        reset gw and config it to tester mode
        """
        self.GwObj.reset_gw()
        time.sleep(1)
        self.GwObj.write('!set_tester_mode 1')
        time.sleep(0.002)
        self.GwObj.write('!enable_brg_mgmt 0')
        time.sleep(0.002)
        self.GwObj.write('!listen_to_tag_only 1')
        time.sleep(0.002)

        self.GwObj.config_gw(rssi_thr_val=int(self.selected_test['rssiThresholdHW']),
                             pl_delay_val=self.selected_test['plDelay'], start_gw_app=False)

    def wait_for_trigger(self, wait_for_gw_trigger):
        """
        wait for gw trigger, i.e. send 'Start Production Line' msg
        :param wait_for_gw_trigger: the time [seconds] to wait to trigger,
                                    if the elapsed time is larger the function return False
        :type wait_for_gw_trigger: int
        :return: if trigger was detected return True
        :rtype: bool
        """
        gw_answer = ''
        gw_trigger_init = datetime.datetime.now()
        dt = datetime.datetime.now() - gw_trigger_init
        while gw_answer == '' and not self.stop_event_trig.isSet() and dt.total_seconds() < wait_for_gw_trigger:
            gw_answer = self.GwObj.read_specific_message(msg="Start Production Line GW", read_timeout=1)
            dt = datetime.datetime.now() - gw_trigger_init
        return "Start Production Line GW" in gw_answer

    def power_index_to_value(self, power_index, abs_power=False, gw_output=False):
        """
        convert gw ouput power index to value according to valid_output_power_vals
        :param power_index: the index of the valid_output_power_vals list
        :type power_index: int
        :param abs_power: true if the desired value is the absolute output power value
        :type abs_power: bool
        :param gw_output: true if the desired value is the gw command output power value
        :type gw_output: bool
        :return: the desired value
        :rtype: int or str
        """
        all_power = self.GwObj.valid_output_power_vals
        if abs_power:
            return all_power[power_index]['abs_power']
        if gw_output:
            return all_power[power_index]['gw_output_power']

    def end_of_time(self, timer_type=''):
        """
        trigger when the test timers are set (the defined test time was elapsed)
        and reset the timers
        :param timer_type: the timer name
        :type timer_type: str
        """
        self._printing_func('{} time has expired'.format(timer_type), logger_name=LoggerName.RESULTS)
        self.time_expired = True
        self.reset_timers()

    def packet_filter(self, packet_list, filter_param='rssi', param_limits=None):
        """
        filter the packets from the packet_list according to the filter_param and the param_limits.
        packets that were filtered out of the test does no take into account during the test and considered as noise
        :param packet_list: the incoming packets list
        :type packet_list: PacketList
        :param filter_param: one of the packet dataframe column names
        :type filter_param: str
        :param param_limits: list of two elements [x, y] that defines the range of the valid param (x,y including)
        :type param_limits: list
        :return: the filtered packet list
        :rtype: PacketList
        """

        def update_custom_data(packet, key, value):
            if key in packet.custom_data.keys():
                packet.custom_data[key][-1] = value
            else:
                packet.custom_data[key] = [value]

        if param_limits is None:
            param_limits = [0, float('inf')]
        filtered_packet_list = PacketList()

        for p in packet_list:
            # filter packets from black list:
            if p.packet_data['adv_address'] in self.black_list:
                p.add_custom_data(custom_data={'packet_status': 'blacklist'})
            else:
                # filter packets by filter param:
                packet_param_list = p.extract_packet_data_by_name(filter_param)
                sprinkler_ids = []
                for i, param in enumerate(packet_param_list):
                    if param_limits[0] <= param <= param_limits[-1]:
                        update_custom_data(p, 'packet_status', 'good')
                        sprinkler_ids.append(i)
                    else:
                        update_custom_data(p, 'packet_status', filter_param)

                if len(sprinkler_ids) > 0:
                    filtered_packet_list.append(p.filter_by_sprinkler_id(sprinkler_ids=sprinkler_ids))

        return filtered_packet_list

    def select_tag_under_test(self, optional_tags):
        """
        select which tag is under test even if more than one tag sends packets
        :param optional_tags: all tags that transmits during the tag-test
        :type optional_tags: list
        :return: the packet list of the selected tag under test
        :rtype: PacketList
        """
        self.tag_results.all_tags = self.tag_results.add_packets_to_multi_tags(packets_in=self.tag_results.all_packets,
                                                                               multi_tag_out=self.tag_results.all_tags)
        self._printing_func('Starting to decide which tag is under test')
        if len(optional_tags) == 0:
            print('we are not supposed to get here - test ends without stop criteria')
        elif len(optional_tags) == 1:
            self.tag_results.selected_tag = self.tag_results.all_tags.tags[optional_tags[0]]
        else:  # more than one tag reach the stop criteria:
            tags_in_tie = False
            min_rssi = None
            max_size = None
            selected_adva = None
            for adva in optional_tags:
                cur_mean_rssi = self.tag_results.filtered_tags.get_avg_rssi_by_id(id=adva)
                if min_rssi is None or cur_mean_rssi < min_rssi:  # best tag
                    min_rssi = cur_mean_rssi
                    max_size = self.tag_results.filtered_tags.tags[adva].size()
                    selected_adva = adva
                elif min_rssi is not None and cur_mean_rssi == min_rssi:  # tiebreak between tags
                    if self.tag_results.filtered_tags.tags[adva].size() > max_size:
                        max_size = self.tag_results.filtered_tags.tags[adva].size()
                        selected_adva = adva
                    if self.tag_results.filtered_tags.tags[adva].size() == max_size:
                        self._printing_func('we cannot select which tag is under test since both tags: {}, {} have '
                                            'the same rssi mean and number of packets'.format(adva, selected_adva))
                        tags_in_tie = True
                elif min_rssi is not None and cur_mean_rssi > min_rssi:  # noisy tag
                    self.black_list.append(adva)
                    self._printing_func('tag: {} was added to blacklist'.format(adva))

            if selected_adva is None:
                msg = 'no rssi was found for the selected packets'
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception(msg)
            elif tags_in_tie:
                pass
            else:
                self.tag_results.selected_tag = self.tag_results.all_tags.tags[selected_adva]

        return self.tag_results.selected_tag

    def get_packets(self, filter_param='rssi', filter_value=0):
        """
        receive packets from the gw (via the listener) and filter them according to packet_filter()
        :param filter_param: one of the packet dataframe column names (for packet_filter)
        :type filter_param: str
        :param filter_value: the max valid value of the specified param
        :type filter_value: int
        :return: True if packet were received
        :rtype: bool
        """
        packets_received_list = None
        if self.GwObj.is_data_available():
            packets_received_list = self.GwObj.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                           data_type=DataType.TAGS_STAT,
                                                           tag_inlay=self.selected_test['inlay'])
        if packets_received_list:
            self._printing_func('got {} packets'.format([p.get_packet_string() for p in packets_received_list]),
                                log_level=logging.DEBUG)
            filtered_packets = self.packet_filter(packets_received_list, filter_param=filter_param,
                                                  param_limits=[0, filter_value])
            self.tag_results.all_packets.__add__(packets_received_list)
            if filtered_packets.size():
                self.tag_results.filtered_tags = \
                    self.tag_results.add_packets_to_multi_tags(filtered_packets, self.tag_results.filtered_tags)
                self._printing_func('and {} pass the packet filter'.format(
                    [p.get_packet_string() for p in filtered_packets]), log_level=logging.DEBUG)
            return True
        else:
            return False

    def check_stop_criteria(self, stop_criteria_dict=None):
        """
        check if the received packet met the stop criteria and the test should be stopped
        :param stop_criteria_dict: dictionary according to the test suite definition, (e.g. {"num_packets": [1, 99]})
        :type stop_criteria_dict: dict
        :return: the tags which reached the stop criteria
        :rtype: list
        """

        if stop_criteria_dict == {}:
            return []
        tags_stat_df = self.tag_results.filtered_tags.get_statistics()
        tags_reached_criteria = []
        if tags_stat_df.size > 0:
            for _, tag in tags_stat_df.iterrows():
                try:
                    criteria_status = [v[0] <= tag[k] <= v[-1] for k, v in stop_criteria_dict.items()]
                    if all(criteria_status):
                        tags_reached_criteria.append(tag['adv_address'])
                except Exception as e:
                    raise e

        return tags_reached_criteria

    @staticmethod
    def is_gw_fetal_error(packet_list):
        """
        check if the gw reset itself for some reason
        :param packet_list: the received packets list
        :type packet_list: PacketList
        :return:
        :rtype:
        """
        counter = 0
        for p in packet_list:
            if p.gw_data['stat_param'].size > 1:
                for s in p.gw_data['stat_param']:
                    if s == 0:
                        counter = counter + 1
                        if counter > 1:
                            return True
            else:
                if p.gw_data['stat_param'] == 0:
                    counter = counter + 1
                    if counter > 1:
                        return True
        return False

    def statistics_analyzer(self, test_param=None, test_num=None):
        """
        test the quality of the test according to test_param
        :param test_param: the test parameters including the quality parameters which defines if
                           the tag passed or failed the test (e.g.
        :type test_param: dict
        :param test_num: the test number
        :type test_num: int
        :return: True if the tag passed the test
        :rtype: bool
        """

        # add test num to the packets:
        self.tag_results.add_selected_tag_statistics(custom_data={'test_num': test_num})
        if self.is_gw_fetal_error(self.tag_results.selected_tag):
            self.gw_reset_and_config()
            self.tag_results.test_status = FailureCodes.GW_ERROR
            targets_status = [False]
        elif 'quality_param' in test_param and len(test_param['quality_param']) > 0:
            targets_status = [v[0] <= self.tag_results.selected_tag_statistics[k] <= v[-1]
                              for k, v in test_param['quality_param'].items()]
            self.logger_results.debug('selected tag values: {}'.format({k: self.tag_results.selected_tag_statistics[k]
                                                                        for k in test_param['quality_param'].keys()
                                                                        }))
            self.tag_results.set_quality_test_failure(test_param['quality_param'], targets_status)

        else:
            targets_status = [True]

        return all(targets_status)

    def init_test(self, sub_test, is_start_gw_app=True):
        """
        initialize the test
        :param sub_test: the test parameter according to the test suite definition
        :type sub_test: dict
        :param is_start_gw_app: if True, the gw starts its application (transmit and receive)
        :type is_start_gw_app: bool
        """
        self.test_end = False
        self.time_expired = False

        self.logger_results.info(
            'Input parameters for GW:\nStage name : {}\nPattern '
            ': {}\nTime Profile : {}\nGW Power : {}dBm\nsub1G Power : {}dBm\n-----------------------'
            '--------------------------------------------------'.format(
                sub_test['name'], sub_test['energizingPattern'], sub_test['timeProfile'],
                sub_test['gw_power_dict']['abs_power'], sub_test['sub1g_power']))

        # Config GW according to Test Suite
        self.GwObj.start_continuous_listener()
        self.GwObj.reset_listener()
        self.GwObj.config_gw(energy_pattern_val=sub_test['energizingPattern'],
                             received_channel=int(sub_test['rxChannel']),
                             time_profile_val=sub_test['timeProfile'],
                             effective_output_power_val=sub_test['gw_power_dict']['abs_power'],
                             sub1g_output_power_val=sub_test['sub1g_power'],
                             start_gw_app=is_start_gw_app)
        # doc config param
        self.tag_results.add_run_data(test_param=sub_test)

    def init_test_timers(self, max_ttfp, sub_test):
        """
        initialize the test timers - the whole test timer and the timer for ttfp if specified
        :param max_ttfp: the maximal ttfp (i.e. time to first packet) to wait before failing the test [in seconds]
        :type max_ttfp: float
        :param sub_test: the test parameters according to the test suite
        :type sub_test: dict
        """
        if max_ttfp is not None:
            self.first_packet_timer = threading.Timer(max_ttfp, self.end_of_time, ['First Packet'])
            self.first_packet_timer.start()
            self.logger.info('Timer for ttfp has been set {} seconds'.format(max_ttfp))
        self.test_timer = threading.Timer(sub_test['maxTime'], self.end_of_time, ['Test'])
        self.test_timer.start()
        self.logger.info('Timer for test has been set {} seconds'.format(sub_test['maxTime']))

    def reset_timers(self, only_first_packet_timer=False):
        """
        reset the test timers
        :param only_first_packet_timer: if True only the ttfp timer is reset
        :type only_first_packet_timer: bool
        :return:
        :rtype:
        """
        if self.first_packet_timer:
            self.first_packet_timer.cancel()
        if not only_first_packet_timer:
            self.test_timer.cancel()

    def _printing_func(self, msg, logger_name=LoggerName.MAIN, log_level=logging.INFO):
        """
        internal function to print the logs
        :param msg: the message to print
        :type msg: str
        :param logger_name: the logger name
        :type logger_name: LoggerName
        :param log_level: the log level
        :type log_level: logging
        """
        if self.verbose or log_level != logging.DEBUG:
            with self._lock_print:
                if logger_name.value == 'main':
                    self.logger.log(log_level, msg)
                elif logger_name.value == 'gw':
                    self.logger_gw.log(log_level, msg)
                elif logger_name.value == 'results':
                    self.logger_results.log(log_level, msg)

    def add_to_blacklist(self, new_blacklist):
        """
        add tags advertising address to the black list
        :param new_blacklist: new tag id to add to the black list
        :type new_blacklist: str or list
        """
        if isinstance(new_blacklist, list):
            self.black_list += new_blacklist
        elif isinstance(new_blacklist, str):
            self.black_list.append(new_blacklist)
        else:
            raise Exception('trying to add new member to black list of unsupported type: {}'.format(new_blacklist))

    def run(self, wait_for_gw_trigger=None, max_ttfp=None):
        """
        Flow:
        1. wait for trigger if wait_for_gw_trigger is specified.
        2. Collect filtered packets (e.g. filtered by rssi)
        3. Check if we reached stop criteria - according to stop criteria list
        4. Check if test passed according to performance criteria:
            A. identify the tag under test
            B. test the selected tag performance

        Stop Criteria list:
        1. test time expired
        2. time to first packet expired if max_ttfp is specified
        3. external stop event, is stop_event_trig was specified whn init the class
        4. parameter according to the tests_suite.json (e.g. number of packets)

        :param wait_for_gw_trigger: if specified, the test waits the specified seconds for the gw trigger and
                                    starts only when triggered
        :type wait_for_gw_trigger: float or NoneType
        :param max_ttfp: the maximum time in seconds to wait for the first packet
        :type max_ttfp: int or NoneType
        :return: the test results including all the tags and test information
        :rtype: WiliotTesterTagResultList
        """

        self._printing_func('New tag test starts from API', logger_name=LoggerName.RESULTS)
        self.test_results = WiliotTesterTagResultList()
        # init first stage:
        self.tag_results = WiliotTesterTagResult()
        self.init_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)

        # wait for trigger if needed
        if wait_for_gw_trigger is None:
            self.start_test = True
        else:
            self._printing_func('Wait for GW trigger for {} second'.format(wait_for_gw_trigger))
            self.start_test = self.wait_for_trigger(wait_for_gw_trigger)

        # check if test can be started:
        if self.stop_event_trig.isSet():
            self._printing_func('Run was stopped by the stop event before it started', log_level=logging.INFO)
            self.GwObj.stop_continuous_listener()
            return self.test_results

        if not self.start_test:
            self._printing_func('no trigger was detected. Please check GW for input trigger', log_level=logging.INFO)
            self.GwObj.stop_continuous_listener()
            return self.test_results

        self.test_results.set_trigger_time()
        self.GwObj.reset_listener()
        # Test begins
        self._printing_func('Trigger received')

        num_of_tests = len(self.selected_test['tests'])
        for test_num in range(num_of_tests):
            sub_test = self.selected_test['tests'][test_num]

            # init sub-test
            self._printing_func('---------------------Started stage {} out of {} stages-----------------------'.
                                format(test_num + 1, num_of_tests), logger_name=LoggerName.RESULTS)
            if test_num:
                self.tag_results = WiliotTesterTagResult()
                self.init_test(sub_test=sub_test)

            self.tag_results.test_start = datetime.datetime.now()
            # Begin test timers
            self.init_test_timers(max_ttfp, sub_test)

            # Start test check
            tags_reached_criteria = []
            while not self.test_end and not self.stop_event_trig.isSet() and not self.time_expired:
                # collect filtered packets
                is_received_packet = self.get_packets(filter_param='rssi',
                                                      filter_value=self.selected_test['rssiThresholdSW'])
                if is_received_packet:
                    self.reset_timers(only_first_packet_timer=True)
                    # check if we reached stop criteria:
                    tags_reached_criteria = self.check_stop_criteria(stop_criteria_dict=sub_test['stop_criteria'])

                    if len(tags_reached_criteria):
                        self._printing_func('test reached stop criteria - starting to analyze the results')
                        self.test_end = True
                else:
                    time.sleep(0)  # allow time for recovery

            # stop gw from transmitting
            # self.GwObj.config_gw(time_profile_val=[0, sub_test['timeProfile'][-1]], start_gw_app=False)
            self.GwObj.stop_gw_app()

            # check why the test is over
            if self.stop_event_trig.isSet():  # Stop event was triggered
                self._printing_func('Stop was triggered', log_level=logging.INFO)
                self._printing_func('Tag marked as Fail', logger_name=LoggerName.RESULTS)
                self.reset_timers()
                self.tag_results.test_status = FailureCodes.STOP_BY_USER
                self.test_results.append(self.tag_results)

            elif self.time_expired:  # time expired before reaching stop criteria
                if sub_test['stop_criteria']:
                    self._printing_func('Stage {} Failed - Timeout'.format(test_num + 1), logger_name=LoggerName.RESULTS)
                    if self.tag_results.all_packets.size() == 0:
                        self.tag_results.test_status = FailureCodes.NO_RESPONSE
                    elif len(self.tag_results.filtered_tags) == 0:
                        self.tag_results.test_status = FailureCodes.NO_PACKETS_UNDER_RSSI_THR
                    else:
                        self.tag_results.test_status = FailureCodes.NOT_ENOUGH_PACKETS
                    self.test_results.append(self.tag_results)
                else:
                    # no stop criteria:
                    self._printing_func('Stage {} Passed Auto (no stop criteria)'.format(test_num + 1),
                                        logger_name=LoggerName.RESULTS)
                    self.tag_results.test_status = FailureCodes.PASS
                    self.test_results.append(self.tag_results)

            elif self.test_end:
                selected_tag = self.select_tag_under_test(optional_tags=tags_reached_criteria)  # Get the best tag
                if selected_tag is not None:
                    self._printing_func('Tag {} was selected'.format(selected_tag[0].packet_data['adv_address']))
                    # selected tag performance:
                    self.tag_results.is_test_passed = self.statistics_analyzer(test_param=sub_test, test_num=test_num)
                    if self.tag_results.is_test_passed:
                        self.tag_results.test_status = FailureCodes.PASS
                        self._printing_func('Stage {} out of {} Passed'.format(test_num + 1, num_of_tests),
                                            logger_name=LoggerName.RESULTS)
                    else:
                        self._printing_func('Tag failed quality test', logger_name=LoggerName.RESULTS,
                                            log_level=logging.DEBUG)
                        self._printing_func('Stage {} out of {} Failed'.format(test_num + 1, num_of_tests),
                                            logger_name=LoggerName.RESULTS)
                else:
                    self.tag_results.test_status = FailureCodes.SEVERAL_TAGS_UNDER_TEST
                    self._printing_func("Couldn't decide which tag transmitting, it will fail")
                self.reset_timers()
                self.test_results.append(self.tag_results)

            else:
                self.reset_timers()
                msg = 'test was stopped due to unknown reason'
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception('test was stopped due to unknown reason')

            # check if delays between stages/sub-test
            if 'delayBeforeNextTest' in sub_test:
                self._printing_func('Going to sleep for {} second '.format(sub_test['delayBeforeNextTest']))
                time.sleep(int(sub_test['delayBeforeNextTest']))
            # end of test:
            self.tag_results.test_end = datetime.datetime.now()
            if self.tag_results.test_status != FailureCodes.PASS:
                break  # stop the test if one of the stages was failed

            self.GwObj.stop_continuous_listener()

        self.GwObj.stop_continuous_listener()
        self.reset_timers()
        return self.test_results


if __name__ == '__main__':
    from csv import DictWriter

    from wiliot.wiliot_testers.wiliot_tester_log import WiliotTesterLog
    from wiliot.wiliot_testers.wiliot_tester_tag_result import ConversionTypes, InlayTypes, SurfaceTypes, FailureCodes
    from wiliot.get_version import get_version


    def stop_run():
        my_stop_event.set()


    def dict_to_csv(dict_in, path, append=False, only_titles=False):
        if append:
            method = 'a'
        else:
            method = 'w'
        with open(path, method, newline='') as f:
            dict_writer = DictWriter(f, fieldnames=dict_in.keys())
            if not append:
                dict_writer.writeheader()
            if not only_titles:
                dict_writer.writerow(dict_in)
            f.close()


    def update_run_data(run_data_path, run_data, res=None, save_to_csv=True):
        if res is not None:
            run_data['total_run_tested'] += 1
            run_data['total_run_passed_offline'] += res.get_total_test_status()
            run_data['run_responsive_tags_yield'] = \
                (run_data['total_run_responding_tags'] / run_data['total_run_tested']) * 100
            run_data['run_offline_yield'] = \
                (run_data['total_run_passed_offline'] / run_data['total_run_tested']) * 100

        if save_to_csv:
            dict_to_csv(dict_in=run_data, path=run_data_path)


    def update_packet_data(packets_data_path, res=None, test_data=None, only_titles=False):

        def save_default_packet_data(summary=None):
            default_data = {'raw_packet': None, 'adv_address': None, 'decrypted_packet_type': None,
                            'group_id': None, 'flow_ver': None,
                            'test_mode': None, 'en': None, 'type': None, 'data_uid': None, 'nonce': None,
                            'enc_uid': None, 'mic': None, 'enc_payload': None, 'gw_packet': None, 'rssi': None,
                            'stat_param': None, 'time_from_start': None, 'counter_tag': None,
                            'is_valid_tag_packet': None, 'common_run_name': test_data['common_run_name'],
                            'tag_run_location': test_data['tag_run_location'],
                            'total_test_duration': None, 'total_location_duration': None, 'status_offline': None,
                            'fail_bin': test_data['fail_bin'], 'fail_bin_str': test_data['fail_bin_str'],
                            'external_id': None,
                            'qr_validated': test_data['qr_validated'], 'test_num': test_data['test_num'],
                            'trigger_time': test_data['trigger_time'], 'packet_status': None}
            if summary is None:
                default_sum = {'is_test_pass': None, 'selected_tag': None, 'test_start_time': None,
                               'test_end_time': None, 'test_status': None, 'rx_channel': None,
                               'energizing_pattern': None, 'time_profile': None, 'num_packets': 0,
                               'num_cycles': 0, 'sprinkler_counter_mean': None, 'sprinkler_counter_std': None,
                               'sprinkler_counter_min': None, 'sprinkler_counter_max': None, 'tbp_mean': None,
                               'tbp_std': None, 'tbp_min': None, 'tbp_max': None, 'tbp_num_vals': None,
                               'per_mean': None, 'per_std': None, 'rssi_mean': None, 'rssi_std': None,
                               'rssi_min': None, 'rssi_max': None, 'ttfp': None, 'rx_rate_normalized': None,
                               'rx_rate': None}
            else:
                default_sum = summary

            default_packet_att = {'is_valid_packet': None, 'inlay_type': None}
            default_dict = {**default_data, **default_sum, **default_packet_att}
            default_ordered_dict = {k: default_dict[k] for k in packet_headers_default}
            dict_to_csv(dict_in=default_ordered_dict, path=packets_data_path, append=(not only_titles),
                        only_titles=only_titles)

        if res is not None:
            test_data['status_offline'] = int(res.get_total_test_status())
            test_data['total_test_duration'] = res.get_total_test_duration()
            test_data['fail_bin'] = res.get_total_fail_bin()
            test_data['fail_bin_str'] = res.get_total_fail_bin(as_name=True)
            test_data['trigger_time'] = res.get_trigger_time()
            for i, r in enumerate(res):
                test_data['test_num'] = i
                r_sum = r.get_summary()

                # add packets info:
                if r.all_packets.size():
                    # we received packets
                    for p in r.all_packets:
                        p.add_custom_data(
                            custom_data={**test_data, **r_sum})
                    r.all_packets.to_csv(path=packets_data_path, append=True, export_packet_id=False,
                                         columns=packet_headers_default)
                else:
                    # no responds in current test
                    save_default_packet_data(summary=r_sum)

        else:
            test_data['test_num'] = 0
            save_default_packet_data()


    log_path = 'C:\\Users\\shunit\\Downloads'
    black_list = ['A', 'B']
    test_suite = {"Dual Band": {
        "plDelay": 100,
        "rssiThresholdHW": 95,
        "rssiThresholdSW": 80,
        "maxTtfp": 5,
        "tests": [
            {"name": "first_packets_ble_band",
             "rxChannel": 37,
             "energizingPattern": 18,
             "timeProfile": [5, 10],
             "absGwTxPowerIndex": -1,
             "maxTime": 5,
             "delayBeforeNextTest": 0,
             "stop_criteria": {"num_packets": [1, 99]},
             "quality_param":
                 {
                     "ttfp": [0, 5]
                 }
             },
            {"name": "sub1G_band",
             "rxChannel": 37,
             "energizingPattern": 52,
             "timeProfile": [5, 10],
             "absGwTxPowerIndex": -1,
             "sub1gGwTxPower": 9,
             "maxTime": 5,
             "stop_criteria": {"num_packets": [2, 99]},
             "quality_param":
                 {
                 }
             }
        ]
    }}
    run_data = {'common_run_name': 'test_test', 'tester_station_name': 'Wiliot',
                'operator': 'Shunit', 'reel_run_start_time': None, 'reel_run_end_time': None,
                'batch_name': 'reel1', 'tester_type': 'offline', 'comments': '',
                'total_run_tested': 0, 'total_run_responding_tags': 0,
                'total_run_passed_offline': 0,
                'total_missing_labels': 0, 'run_responsive_tags_yield': float('nan'),
                'run_offline_yield': float('nan'), 'ttfp_avg': float('nan'),
                'conversion_type': ConversionTypes.STANDARD.value, 'inlay': InlayTypes.TEO_086.value,
                'test_suite': list(test_suite.keys())[0], 'test_suite_dict': test_suite,
                'surface': SurfaceTypes.AIR.value, 'to_print': True, 'qr_validation': True,
                'print_pass_job_name': 'job_name', 'printing_format': 'SGTIN',
                'external_id_prefix': 'aaa',
                'external_id_suffix_init_value': 0,
                'coupler_partnumber': 'abcd',
                'gw_version': None, 'py_wiliot_version': get_version(), 'upload_date': None, 'owner_id': 'wiliot-ops'}
    packet_headers_default = ['common_run_name', 'tag_run_location', 'test_num', 'external_id',
                              'time_from_start', 'raw_packet', 'rssi', 'packet_status', 'adv_address',
                              'selected_tag',
                              'is_test_pass', 'status_offline', 'fail_bin', 'fail_bin_str', 'test_status',
                              'num_packets', 'num_cycles', 'sprinkler_counter_mean', 'sprinkler_counter_std',
                              'sprinkler_counter_min', 'sprinkler_counter_max', 'tbp_mean', 'tbp_std',
                              'tbp_min', 'tbp_max', 'tbp_num_vals', 'per_mean', 'per_std', 'rssi_mean',
                              'rssi_std', 'rssi_min', 'rssi_max', 'ttfp', 'rx_rate_normalized', 'rx_rate',
                              'total_test_duration', 'total_location_duration', 'test_start_time',
                              'trigger_time', 'test_end_time',
                              'qr_validated', 'rx_channel', 'energizing_pattern', 'time_profile',
                              'decrypted_packet_type', 'group_id', 'flow_ver', 'test_mode', 'en',
                              'type', 'data_uid', 'nonce', 'enc_uid', 'mic', 'enc_payload', 'gw_packet',
                              'stat_param']
    run_name = run_data['common_run_name'] + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    my_logger = WiliotTesterLog(run_name=run_name)
    my_logger.set_logger(log_path=log_path)

    my_logger.create_data_dir(data_path=log_path, tester_name='offline', run_name=run_name)
    my_stop_event = threading.Event()

    wiliot_tag_test = WiliotTesterTagTest(selected_test='Dual Band', test_suite=test_suite,
                                          stop_event_trig=my_stop_event,
                                          logger_name=my_logger.logger.name,
                                          logger_result_name=my_logger.results_logger.name,
                                          logger_gw_name=my_logger.gw_logger.name,
                                          black_list=black_list,
                                          inlay=run_data['inlay'])

    run_data['gw_version'] = wiliot_tag_test.get_gw_version()
    wait_for_gw_trigger = None
    max_ttfp = test_suite['Dual Band']['maxTtfp']
    cont_run = True

    my_timer = threading.Timer(20, stop_run)
    my_timer.start()
    missing_label = False
    run_data['reel_run_start_time'] = datetime.datetime.now()
    test_data = {'common_run_name': run_data['common_run_name'], 'tag_run_location': 0, 'total_test_duration': None,
                 'total_location_duration': None,
                 'status_offline': False, 'fail_bin': FailureCodes.NONE.value, 'fail_bin_str': FailureCodes.NONE.name,
                 'external_id': 0, 'qr_validated': True,
                 'test_num': 0, 'trigger_time': None}
    # update data files
    update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data)
    update_packet_data(packets_data_path=my_logger.packets_data_path, only_titles=True, test_data=test_data)
    all_tags = []
    ttfp_num = 0
    ttfp_sum = 0
    while cont_run:
        # init test data:
        loc_start_time = datetime.datetime.now()
        test_data['total_test_duration'] = None
        test_data['status_offline'] = False
        # check if tag exists at the test env
        if missing_label:
            # TODO add here the logic for missing label
            run_data['total_missing_labels'] = run_data['total_missing_labels'] + 1
            test_data['fail_bin'] = FailureCodes.MISSING_LABEL.value
            test_data['tag_run_location'] = test_data['tag_run_location'] + 1

            update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data)
            update_packet_data(packets_data_path=my_logger.packets_data_path, test_data=test_data)
            continue
        # ##################### test the tag ############################## #
        res = wiliot_tag_test.run(wait_for_gw_trigger=wait_for_gw_trigger, max_ttfp=max_ttfp)
        if res.is_results_empty():
            my_timer.cancel()
            raise Exception('Test was stopped before it started due to some reason')
        # ##################### test the tag ############################## #
        if res.is_all_tests_passed():
            print('********* PASS ************')
        # add ttfp avg:
        for r in res:
            if 'ttfp' in r.selected_tag_statistics:
                ttfp_sum = ttfp_sum + r.selected_tag_statistics['ttfp']
                ttfp_num = ttfp_num + 1

            # for p in r.all_packets:
            #     print('packet: {}, len:{}, status: {}'.format(p.packet_data['raw_packet'], len(p),
            #                                                   p.custom_data['packet_status']))
        if ttfp_num:
            run_data['ttfp_avg'] = ttfp_sum / ttfp_num

        # TODO move machine to the next tag
        total_loc_time = datetime.datetime.now() - loc_start_time
        test_data['total_location_duration'] = total_loc_time.total_seconds()
        # check duplication:
        selected_tag = res.check_and_get_selected_tag_id()
        if selected_tag != '':
            if selected_tag in all_tags:
                res.set_total_fail_bin(FailureCodes.DUPLICATION_OFFLINE)
                res.set_total_test_status(status=False)
                wiliot_tag_test.add_to_blacklist(selected_tag)
                res.set_packet_status(adv_address=selected_tag, status='duplication')
            else:
                all_tags.append(selected_tag)
                run_data['total_run_responding_tags'] += 1

        # add packets to packet_data.csv:
        update_packet_data(res=res, packets_data_path=my_logger.packets_data_path, test_data=test_data)
        # update run_data:
        update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data, res=res)

        if my_stop_event.isSet():
            cont_run = False
            my_timer.cancel()

        # end of tag test actions
        test_data['tag_run_location'] = test_data['tag_run_location'] + 1
        if res.is_all_tests_passed():
            test_data['external_id'] = test_data['external_id'] + 1

        time.sleep(0)

    run_data['reel_run_end_time'] = datetime.datetime.now()
    run_data['upload_date'] = datetime.datetime.now()
    dict_to_csv(run_data, path=my_logger.run_data_path)
    # upload data to cloud
    # TODO add here function to upload data to database/cloud
    print('blacklist: {}'.format(wiliot_tag_test.black_list))
    print('done')
