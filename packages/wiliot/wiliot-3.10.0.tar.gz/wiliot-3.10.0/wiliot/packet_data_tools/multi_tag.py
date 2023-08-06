import numpy as np
import pandas
import pandas as pd
import copy

from wiliot.packet_data_tools.packet import Packet
from wiliot.packet_data_tools.packet_list import PacketList


class MultiTag(dict):
    def __init__(self):
        self.tags = {}  # key is adv_address, value is Packet_list

    def __len__(self):
        """
        Amount of tags
        """
        return len(self.tags)

    def __add__(self, other_multi_tag):
        """
        merge 2 MultiTag object using '+' sign: multi_tag1+multi_tag2

        :type other_multi_tag: MultiTag
        :param other_multi_tag:

        :return: merged other_multi_tag, not mandatory
        """
        for id in other_multi_tag.keys():
            if id not in self.tags.keys():
                self.tags[id] = other_multi_tag[id].copy()
            else:
                self.tags[id] = self.tags[id] + other_multi_tag[id]
        return self

    def copy(self):
        return copy.deepcopy(self)

    def append(self, packet, ignore_sprinkler=False, packet_list_obj=PacketList, packets_id=None) -> None:
        """
        Adds single Packet to MultiTag

        :type packet: Packet or DecryptedPacket
        :param packet: packet to be added to packet_list
        :type ignore_sprinkler: Bool
        :param ignore_sprinkler: allow duplicates packets from different sprinkler
        :type packet_list_obj: PacketList or DecryptedPacketList
        :param packet_list_obj: the packet list object (encrypted or decrypted)
        :type packets_id: str
        :param packets_id: the tags id which define the multi tag structure (accoridng to adv address, uid, ..)

        :return: None
        """
        if packets_id is None:
            packets_id = packet.packet_data['adv_address']

        if packets_id not in self.tags.keys():
            self.tags[packets_id] = packet_list_obj().copy()

        self.tags[packets_id].append(packet, ignore_sprinkler)

    def dump(self, packet_dict_list: list):
        """
        gets list of raw_packet or packet_dict and fill packet_list with data

        :type packet_dict_list: list
        :param packet_dict_list: gw list (get_data), fill packet_list with data

        :return: bool status
        """
        try:
            for packet_dict in packet_dict_list:
                packet = Packet(packet_dict)
                if packet.is_valid_packet:
                    self.print_live_stream(packet)
                    self.append(packet)
            return True
        except:
            return False

    def print_live_stream(self, packet):
        """
        for future use - implement output
        """
        # set parameters to filter view by
        pass

    def get_statistics_by_id(self, id):
        """
        Calculates statistics of self.
        @return dictionary with predefined statistics of the packetList.
        """
        return self.tags[id].get_statistics()

    def get_avg_rssi_by_id(self, id=''):
        """
        return tag average rssi (4 decimal points accuracy)
        :type id: str
        :param id: adv_address or tag_id of wanted tag
        :return: average rssi for tag
        """
        return self.tags[id].get_avg_rssi()

    def get_avg_tbp_by_id(self, id='', ignore_outliers=False):
        """
        return tag average tbp (4 decimal points accuracy)
        :param ignore_outliers: reject data outside the 2 std area
        :type ignore_outliers: bool
        :type id: str
        :param id: adv_address or tag id of wanted tag

        :return: average tbp for tag
        """
        return self.tags[id].get_avg_tbp(ignore_outliers=ignore_outliers)

    def to_csv(self, path, id_name='adv_address'):
        statistics_df = self.get_statistics(id_name=id_name)
        statistics_df.to_csv(path)

    def get_statistics(self, id_name='adv_address'):
        statistics_df = pd.DataFrame()
        for id in self.tags.keys():
            id_statistics = self.get_statistics_by_id(id)
            id_statistics[id_name] = id
            id_statistics_df = pd.DataFrame(id_statistics, index=[0])
            statistics_df = pd.concat([statistics_df, id_statistics_df], axis=0)
        return statistics_df

    def get_statistics_list(self, attributes=['adv_address', 'num_cycles', 'num_packets', 'tbp_mean', 'rssi_mean']):
        statistics_df = self.get_statistics()
        statistics_list = []
        specific_statistics_df = statistics_df[attributes]

        for index, row in specific_statistics_df.iterrows():
            dict = {}
            for att in attributes:
                dict[att] = row[att]
            statistics_list.append(dict.copy())

        return statistics_list


if __name__ == '__main__':
    from test_packet_list import p_list

    packet_list1 = PacketList()
    # packet_list2 = PacketList()
    packet_list1.dump(p_list)
    #
    # packet_list3 = packet_list1 + packet_list2

    mt = MultiTag()
    for packet in packet_list1.packet_list[:7]:
        mt.append(packet)

    mt2 = MultiTag()
    mt2.dump(p_list)

    m3 = mt + mt2
    a = m3.get_statistics_list()
    pass
