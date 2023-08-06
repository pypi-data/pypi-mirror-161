import os
import time
import pyvisa
import logging

RANGE = 'AUTO'


class KeySight34465A:
    """
    Base class for the Keysight 34465A DMM
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    def __init__(self, connection_string):
        self.dmm = None
        self.connection_string = connection_string
        self.resource_manager = None

    def open_connection(self):
        """
        Opens a TCP/IP connection to connect to the Keysight DMM 34465A
        """
        self.resource_manager = pyvisa.ResourceManager()
        self.connection_string = os.getenv("DMM_CONNECTION_STRING", default='TCPIP0::192.168.123.200::INSTR')
        try:
            logging.info(f": Opening KeysightDMM 34465A Resource at {self.connection_string}")
            self.dmm = self.resource_manager.open_resource(self.connection_string)
            self.dmm.read_termination = '\n'
            self.dmm.write_termination = '\n'
            time.sleep(3)
        except Exception as err:
            raise Exception(f": ERROR {err}: Could not open connection! ")

    def close_connection(self):
        """
        Closes the TCP/IP connection to the Keysight DMM 34465A
        """
        self.resource_manager.close()

    def self_test(self):
        """
        Performs the self-test and checks for system errors
        :return: Boolean: True or Error
        """
        sys_err = self.dmm.query(f'SYST:ERR?', delay=1)
        if sys_err == '+0,"No error"':
            try:
                selftest = self.dmm.query(f'TEST:ALL?', delay=1)
                if selftest == "+0":
                    logging.info("PASS: SELF-TEST PASSED!")
                    return True
                else:
                    logging.error(f"Self-test FAILED")
                    return False
            except Exception as e:
                raise Exception(f": ERROR: {e} One or more self-test has FAILED")
        else:
            logging.error(f": SYSTEM_ERROR: {sys_err}")
            raise Exception(f": {sys_err}")

    def id_number(self):
        """
        This function returns the ID number on query in string
        :return: str: ID number
        """
        time.sleep(5)
        idn = self.dmm.query(f'*IDN?', delay=1)
        logging.info(f": IDN: {idn} \n")
        return str(idn)

    def system_info(self):
        """
        This function gets all the system info for the Keysight DMM 34465A
        :return: information in logs
        """

        sys_ver = self.dmm.query(f'SYST:VERS?', delay=1)
        logging.info(f": System Version: {sys_ver}")

        is_dhcp = self.dmm.query(f'SYST:COMM:LAN:DHCP?', delay=1)
        logging.info(f": DHCP Setting: {is_dhcp} \n")

        ip_address = self.dmm.query(f'SYST:COMM:LAN:IPAD?', delay=1)
        logging.info(f": IP Address: {ip_address} \n")

        mac_address = self.dmm.query(f'SYST:COMM:LAN:MAC?', delay=1)
        logging.info(f": MAC Address: {mac_address} \n")

        host_name = self.dmm.query(f'SYST:COMM:LAN:HOST?', delay=1)
        logging.info(f": DNS Hostname: {host_name} \n")

        subnet_mask = self.dmm.query(f'SYST:COMM:LAN:SMASK?', delay=1)
        logging.info(f": Subnet Mask: {subnet_mask} \n")

        dns_setting = self.dmm.query(f'SYST:COMM:LAN:DNS?', delay=1)
        logging.info(f": DNS Setting: {dns_setting} \n")

        gateway = self.dmm.query(f'SYST:COMM:LAN:GAT?', delay=1)
        logging.info(f": Default Gateway: {gateway} \n")

    # def configure_current(self):
    #     """
    #     This function sets all the measurement parameters and trigger parameters to their default values with specified
    #     range and resolution
    #     :param test_mode: AC/DC
    #     :param ranges: {100µA | 1mA | 10mA | 100mA | 1A | 3A | 10A }. Default: AUTO
    #     :param resolution: AC: optional and ignored, fixed to 6 1/2 digits; DC default 10 PLC
    #     :return: Success or failure
    #     """
    #     sys_err = self.dmm.query(f'SYST:ERR?')
    #     time.sleep(2)
    #     if sys_err == '+0,"No error"':
    #         time.sleep(2)
    #         self.dmm.write(f'CONF:CURR:DC AUTO')
    #         self.dmm.write(f'TRIG:SOUR EXT;SLOP POS')
    #         self.dmm.write(f'INIT')
    #         time.sleep(3)
    #         curr = self.dmm.query(f'FETC?')
    #
    #         logging.info(f": DC Current: {curr} Amps \n")
    #         return True
    #     else:
    #         logging.info(f" SYSTEM ERROR: {sys_err}")
    #         raise Exception(f": ERROR: {sys_err}")

    def get_current(self, test_mode):
        """
        This function reads a current measurement
        :param test_mode: AC/DC
        :return: float: Current in Amps
        """
        current = self.dmm.query(f'MEAS:CURR:{test_mode}?', delay=1)
        logging.info(f": {str(test_mode)} Current: {current} Amps \n")
        return float(current)

    # def configure_voltage(self, test_mode, ranges, resolution):
    #     """
    #     This function sets all the measurement parameters and trigger parameters to their default values with specified
    #     range and resolution
    #     :param test_mode: AC/DC
    #     :param ranges: {100 mV | 1 V | 10 V | 100 V | 1000 V}. Default: AUTO
    #     :param resolution: AC: optional and ignored, fixed to 6 1/2 digits; DC default 10 PLC
    #     :return: Success or failure
    #     """
    #     sys_err = self.dmm.query(f'SYST:ERR?')
    #     if sys_err == '+0,"No error"':
    #         conf_volt = self.dmm.query(f'CONF:VOLT:{str(test_mode).upper()} {ranges}, {float(resolution)}')
    #         logging.info(f": {str(test_mode).upper()} Voltage: {conf_volt} Volts \n")
    #         return True
    #     else:
    #         logging.info(f" SYSTEM ERROR: {sys_err}")
    #         raise Exception(f": ERROR: {sys_err}")

    def get_voltage(self, test_mode):
        """
        This function reads a voltage measurement
        :param test_mode: AC/DC
        :return: float: Current in Amps
        """
        voltage = self.dmm.query(f'MEAS:VOLT:{test_mode}?', delay=1)
        logging.info(f": {str(test_mode)} Voltage: {voltage} Volts \n")
        return float(voltage)

    def measurements(self):
        """
        This function takes all the necessary measurements from the DMM
        :return: Values in logs
        """
        frequency = self.dmm.query(f'MEAS:FREQ?', delay=1)
        logging.info(f": Frequency: {frequency} \n")

        period = self.dmm.query(f'MEAS:PER?', delay=1)
        logging.info(f": Period: {period} \n")

        # If the input signal is greater than can be measured on the specified manual range, the instrument displays
        # the word Overload on front panel and returns "9.9E37" from the remote interface.

        diode = self.dmm.query(f'MEAS:DIOD?', delay=1)
        if diode > '+9.8E+37':
            logging.info(f": Check Diode value for Overload of measurement!")
        else:
            logging.info(f": Diode value: {diode} \n")

        resistance = self.dmm.query(f'MEAS:RES?', delay=1)
        if resistance > '+9.80000000E+37':
            logging.info(f": Check Resistance value for Overload of measurement!")
        else:
            logging.info(f": Resistance value: {resistance} \n")

        capacitance = self.dmm.query(f'MEAS:CAP?', delay=1)
        if capacitance > '+9.80000000E+37':
            logging.info(f": Check Capacitance value for Overload of measurement!")
        else:
            logging.info(f": Capacitance: {capacitance} \n")
