import cantools
import can
import time
import os
import sys
import logging
from tabulate import tabulate
import platform

if platform.system() == "Darwin":
    # TODO (amit, 2021-09-29): remove hacks to support `pcan` when we don't
    #  need it anymore.
    #  Super bad monkey patch to deal with MAC issue:
    #  https://github.com/hardbyte/python-can/issues/1117
    from can.interfaces.pcan import basic

    basic.TPCANMsgMac = basic.TPCANMsg
    basic.TPCANMsgFDMac = basic.TPCANMsgFD
    basic.TPCANTimestampMac = basic.TPCANTimestamp

    from can.interfaces.pcan import pcan

    pcan.TPCANMsgMac = pcan.TPCANMsg
    pcan.TPCANMsgFDMac = pcan.TPCANMsgFD
    pcan.TPCANTimestampMac = pcan.TPCANTimestamp
    # end super bad monkey patch

'''
IsoSPI Interface library
BP_addr is always 1 !
'''

class ISOSPI_Interface:
    """
    This class contains the functions to control the iso spi interface and perform diagnostics
    """
    # logging.basicConfig(filename='cell_emulator_log.txt',
    #                     filemode='a',
    #                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    #                     datefmt='%Y-%m-%d %H:%M:%S',
    #                     level=logging.INFO)

    def __init__(self):
        self.db = cantools.database.load_file(os.path.dirname(os.path.abspath(__file__)) + '/isoSPIInterface.dbc')
        self.bus = None

    def can_connection(self, interface, channel, bitrate):
        can.rc['interface'] = interface
        can.rc['channel'] = channel
        can.rc['bitrate'] = bitrate
        self.bus = can.interface.Bus()

    def get_fw_versions(self):
        """
        This function gets the FW version of the IsoSPI Interfaces
        """
        broadcast_id = 0x600
        logging.info("Using broadcast ID " + hex(broadcast_id))
        # Writing FW Update Request
        msg = can.Message(arbitration_id=broadcast_id,data=[ord('F'), ord('W'), ord('?'), 0, 0, 0, 0, 0],is_extended_id=False)
        print(msg)
        self.bus.send(msg)
        # Block until ready
        fw_versions = self.read_until_RDY()
        logging.info(f"Found {len(fw_versions)} Interfaces ")
        return fw_versions

    def read_until_RDY(self):
        """
        This function sends a command over CAN bus seeking the fw versions of each cell of the interface
        :return: FW versions on each cell of the interface
        """
        wait_time = 1 + time.time()
        msg = self.bus.recv(timeout=2)
        fw_versions = {}
        logging.info("Searching for controllers.")
        while wait_time > time.time():
            fw_versions[msg.arbitration_id] = msg.data[0:6].decode("ASCII")
            msg = self.bus.recv(timeout=1)
        return fw_versions

    def send_command(self,command,wanted=None):
        cmd_message = self.db.get_message_by_name('isoSPI_cntrl')
        data = cmd_message.encode(command, strict=False)
        message = can.Message(arbitration_id=cmd_message.frame_id, data=data,is_extended_id=False)
        self.bus.send(message)
        resp = self.bus.recv(timeout=0.05)
        cnt=0
        data = None
        while resp != None and cnt < 50:
            cnt += 1
            try:
                if resp != None:
                    data = self.db.decode_message(resp.arbitration_id, resp.data)
                    #Check if response is from message
                    if command["BP_addr"] == data["BP_addr"] and command["IF_addr"] == data["IF_addr"]:
                        if wanted is None or wanted in data:
                            break
            except:
                pass
            resp = self.bus.recv(timeout=0.1)
        #print("Recieved " + str(cnt) + " Responses")
        return data


    def enable_hipot(self,interface,port):
        # Hipot Command Multiplexer is 41 dec
        cmd = {'BP_addr': 1 , 'IF_addr': interface , 'IF_port': port, 'command': 41, 'HiPotEnableMain':0, 'HiPotEnable1':1, 'HiPotEnable2':1}
        res = self.send_command(cmd,wanted=f'HiPotEnable1_BP01_IF{str(interface).zfill(2)}')
        logging.debug(res)
        return res

    def disable_hipot(self,interface,port):
        # Hipot Command Multiplexer is 41 dec
        cmd = {'BP_addr': 1 , 'IF_addr': interface , 'IF_port': port, 'command': 41, 'HiPotEnableMain':0, 'HiPotEnable1':0, 'HiPotEnable2':0}
        res = self.send_command(cmd,wanted=f'HiPotEnable1_BP01_IF{str(interface).zfill(2)}')
        logging.debug(res)
        return res

    def disable_mainhipot(self):
        # Hipot Command Multiplexer is 41 dec
        res = []
        cmd = {'BP_addr': 1 , 'IF_addr': 1 , 'IF_port': 0, 'command': 41, 'HiPotEnableMain':0, 'HiPotEnable1':0, 'HiPotEnable2':0}
        res.append(self.send_command(cmd))
        cmd = {'BP_addr': 1 , 'IF_addr': 2 , 'IF_port': 0, 'command': 41, 'HiPotEnableMain':0, 'HiPotEnable1':0, 'HiPotEnable2':0}
        res.append(self.send_command(cmd))
        logging.debug(res)
        return res

    def enable_mainhipot(self):
        # Hipot Command Multiplexer is 41 dec
        res = []
        cmd = {'BP_addr': 1 , 'IF_addr': 1 , 'IF_port': 0, 'command': 41, 'HiPotEnableMain':1, 'HiPotEnable1':0, 'HiPotEnable2':0}
        res.append(self.send_command(cmd))
        cmd = {'BP_addr': 1 , 'IF_addr': 2 , 'IF_port': 0, 'command': 41, 'HiPotEnableMain':1, 'HiPotEnable1':0, 'HiPotEnable2':0}
        res.append(self.send_command(cmd))
        logging.debug(res)
        return res
