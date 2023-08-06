import logging
import os
import time
import pyvisa


def get_class_for_card(name, slot):
    if name == "34925A-1W":
        return KeySight34925A_1W(slot)
    return None


class KeySight34980A:
    """
    Base class for the Keysight 34980A DAQ
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    def __init__(self, connection_string):
        # Supported Devices
        self.resource_manager = None
        self.daq = None
        self.session = None
        self.supported_list = ["34925A-1W"]
        # Cards Can be discovers with : SYSTem:CTYPe? <slot>
        # Should return AGILENT TECHNOLOGIES,<Modellnummer>,<Seriennummer>,<Firmware-Version>
        self.connection_string = connection_string

    def open_connection(self):
        """
        Opens a TCP/IP connection to the Keysight DAQ 34980A
        """
        self.connection_string = os.getenv("DAQ_CONNECTION_STRING", default='TCPIP0::192.168.123.200::INSTR')
        self.resource_manager = pyvisa.ResourceManager()
        try:
            logging.info(f": Opening DAQ Resource at {self.connection_string}")
            self.daq = self.resource_manager.open_resource(self.connection_string)
            self.daq.read_termination = '\n'
            self.daq.write_termination = '\n'
            self.session = self.resource_manager.open_resource(self.connection_string)
            self.session.read_termination = '\n'
            self.session.write_termination = '\n'
        except Exception as e:
            raise Exception(f": ERROR {e}: Could not open Resource\n")
        self.cards = {}
        self.card_types = {}
        for slot in range(8):
            resp = self.daq.query(f'SYSTem:CTYPe? {slot + 1}')
            logging.info(f"Found Module {resp}")
            # print(f"Found Module {resp}")
            type = resp.split(',')[1]
            if type in self.supported_list:
                self.card_types[slot] = type
        logging.info(self.card_types)
        for slot, type in self.card_types.items():
            self.cards[slot] = get_class_for_card(type, slot)

    def close_connection(self):
        """
        Closes the TCP/IP connection to the Keysight DAQ 34980A
        """
        self.resource_manager.close()

    def raw_write(self, cmd):
        return self.daq.write(cmd)

    def raw_query(self, cmd):
        return self.daq.query(cmd)

    def read_channel(self, channel):
        if channel == "0000":
            # print(f"Error measuring net: {net_name} not found, skipping measurement")
            return 0
        else:
            try:
                self.daq.write("CONF:VOLT:DC 10,0.003, (@" + channel + ")")
                self.daq.write("ROUT:SCAN (@" + channel + ")")
                self.daq.write("INIT")
                measured_val = self.daq.query("FETC?")
                return float(measured_val)
            except Exception as e:
                raise Exception(f"ERROR Could not read channel {channel}: {e}")

    def factory_reset(self):
        """
        This function helps factory reset the DAQ
        """
        # System reset
        self.daq.write(f'*RST')

    def id_number(self):
        """
        This function returns the ID number of the equipment
        """
        self.session.write('*IDN?')
        idn = self.session.read()
        logging.info(f': *IDN? returned: {idn}')
        return str(idn)

    def system_info(self):
        """
        This function establishes a connection with the unit under test and gets general information
        from the KeysightDAQ and modules about Manufacturer, ModelNumber,SerialNumber, FirmwareVersion, etc.
        It also gets network information like: IP Address, LAN connectivity, DHCP settings, etc.
        """
        sys_info = {}
        logging.info("######## SYSINFO ########")
        logging.info(': IP: %s\n' %
                     (self.session.get_visa_attribute(pyvisa.constants.VI_ATTR_TCPIP_ADDR)))
        sys_info["IP_Address"] = self.session.get_visa_attribute(pyvisa.constants.VI_ATTR_TCPIP_ADDR)

        safety_interlock = self.daq.query(f'SYSTem:ABUS:INTerlock:SIMulate?')
        logging.info(f": Safety Interlock (0: OFF | 1: ON) {safety_interlock}")
        sys_info['Safety_interlock'] = safety_interlock

        mac_address = self.daq.query(f'SYST:COMM:LAN:MAC?')
        logging.info(f": MAC Address: {mac_address}")
        sys_info["MAC_Address"] = mac_address

        gateway = self.daq.query(f'SYST:COMM:LAN:GATEWAY?')
        logging.info(f": Gateway: {gateway}")
        sys_info['Gateway']= gateway

        host_name = self.daq.query(f'SYST:COMM:LAN:HOST?')
        logging.info(f": Host Name: {host_name}")
        sys_info['Hostname'] = host_name

        dns_address = self.daq.query(f'SYST:COMM:LAN:DNS?')
        logging.info(f": DNS Address: {dns_address}")
        sys_info['DNS_Address'] = dns_address

        domain_name = self.daq.query(f'SYST:COMM:LAN:DOM?')
        logging.info(f": Domain Name: {domain_name}")
        sys_info['Domain_Name'] = domain_name

        dhcp_setting = self.daq.query(f'SYSTem:COMM:LAN:DHCP?')
        logging.info(f": DHCP Setting: {dhcp_setting}")
        sys_info['DHCP_Setting'] = dhcp_setting

        lan_boot_status = self.daq.query(f'SYSTem:COMM:LAN:BST?')
        logging.info(f": LAN boot status: {lan_boot_status}")
        sys_info['LAN_boot_status'] = lan_boot_status

        logging.info("######## SYSINFO ########")
        return sys_info

    def system_status(self):
        """
        This function will run module specific tests one slot at a time
        :return: status
        """
        sys_status = {}
        logging.info("######## SYSTEM STATUS ########")

        # Returns decimal value for the bit number which bits are enabled in the register
        ese_enabled_bits = self.daq.query(f'*ESE?')
        logging.info(f": ESE: Enabled bits in Register: {ese_enabled_bits}")
        sys_status['ESE'] = ese_enabled_bits

        # Returns decimal value for the bit number which is enabled in the Standard Event Register
        esr_enabled_ser = self.daq.query(f'*ESR?')
        logging.info(f": ESR: Enabled Standard Event Register: {esr_enabled_ser}")
        sys_status['ESR'] = esr_enabled_ser

        logging.info("######## SYSTEM STATUS ########")
        return sys_status

    def self_test(self):
        """
        Perform a self-test on the device
        :return: Boolean: Pass or fail
        """
        if not self.daq.query(f'SYST:COMM:LAN:MAC?'):
            raise EnvironmentError(f'ERROR: Keysight DAQ not found!')
        else:
            logging.info(f": Module found : Keysight DAQ 34980A")
        self.session.write('*TST?')
        time.sleep(17)
        self_test = self.session.read()
        if self_test == '+0':
            logging.info(": Self-test Passed!")
            return True
        else:
            raise Exception(f'ERROR in Self-test: Contact Customer Service at Keysight DAQ 34980A')

    def _is_dmm_installed(self):
        """
        This function checks if the internal DMM for the DAQ is installed in the mainframe
        :return Bool: Status
        """
        dmm_installed = self.daq.query(f'INST:DMM:INST?')
        if dmm_installed == 1:
            logging.info(f": DMM is installed in mainframe! ")
            return True
        else:
            logging.error(f": DMM module not found")
            return False

    def _is_dmm_enabled(self):
        """
        This function checks if the internal DMM for the DAQ is enabled
        :return Bool: Status
        """
        try:
            dmm_enabled = self.daq.query(f'INST:DMM?')
            if dmm_enabled == 0:
                logging.info(f": DMM is OFF!")
                return False
            elif dmm_enabled == 1:
                logging.info(f": DMM is ON!")
                return True
        except Exception as e:
            raise Exception(f": {e}")

    def enable_dmm(self):
        """
        This function checks if the internal dmm is present, and is disabled and Enables it
        """
        if self._is_dmm_enabled():
            logging.info(f": Internal DMM already enabled")
            # print(f": Internal DMM already enabled")
            pass
        elif not self._is_dmm_enabled():
            self.daq.write(f'INST:DMM ON')
            logging.info(f": Internal DMM now enabled!")
            # print(f": Internal DMM now enabled!")

    def disable_dmm(self):
        """
        This function checks if the internal dmm is present, and is enabled and Disables it
        """
        if self._is_dmm_enabled():
            self.daq.write(f'INST:DMM OFF')
            logging.info(f": Internal DMM now Disabled!")
            # print(f": Internal DMM now Disabled!")
        elif not self._is_dmm_enabled():
            logging.info(f": Internal DMM already Disabled")
            # print(f": Internal DMM already Disabled")
            pass

    def connect_dmm(self):
        """
        This function will check the status of the internal DMM and connect it
        """
        try:
            _is_dmm_conn = self.daq.query(f'INST:DMM:CONN?')
            if _is_dmm_conn == '0':
                self.daq.write(f'INST:DMM:CONN')
                time.sleep(0.5)
                if self.daq.query(f'INST:DMM:CONN?') == '1':
                    logging.info(f": DMM Connected ")
                    return True
                else:
                    logging.error(f"ERROR: Could not connect DMM")
                    return False
            elif _is_dmm_conn == '1':
                logging.info(f"DMM already connected")
                return True
        except Exception as e:
            raise Exception(f": {e}: trouble reaching DMM. Check installation.")

    def disconnect_dmm(self):
        """
        This function will check the status of the internal DMM and disconnect it
        """
        try:
            _is_dmm_disc = self.daq.query(f'INST:DMM:DISC?')
            if _is_dmm_disc == '0':
                self.daq.write(f'INST:DMM:DISC')
                time.sleep(0.5)
                if self.daq.query(f'INST:DMM:DISC?') == '1':
                    logging.info(f": DMM Disconnected ")
                    return True
                else:
                    logging.error(f"ERROR: Could not disconnect DMM")
                    return False
            elif _is_dmm_disc == '1':
                logging.info(f": DMM already Disconnected ")
                return True
        except Exception as e:
            raise Exception(f": {e}: trouble reaching DMM. Check installation.")

    def get_dmm_voltage(self, test_mode):
        """
        This function measures the internal dmm voltage for AC and DC
        :param test_mode: str: AC/DC
        :return float: DMM voltage in Volts
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_volt = self.daq.query(f'MEAS:VOLT:{str(test_mode).upper()}?')
                logging.info(f": {str(test_mode).upper()} Voltage measurement for the internal DMM: {dmm_volt} V")
                return float(dmm_volt)
            except Exception as e:
                raise Exception(f": {e} Could not get Voltage measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_dmm_current(self, test_mode):
        """
        This function measures the internal dmm AC current
        :param test_mode: str: AC/DC
        :return float: DMM Current in Amps
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_curr = self.daq.query(f'MEAS:CURR:{str(test_mode).upper()}?')
                logging.info(f": {str(test_mode).upper()} Current measurement for the internal DMM: {dmm_curr} A")
                return float(dmm_curr)
            except Exception as e:
                raise Exception(f": {e} Could not get Current measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_dmm_resistance(self, range, resolution):
        """
        This function measures the internal DMM Resistance
        :param range:
        :param resolution:
        :return float: DMM Resistance in Ohms
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_res = self.daq.query(f'MEAS:RES? {int(range)},{int(resolution)}')
                logging.info(f": Resistance measurement for the internal DMM: {dmm_res} Ohms")
                return float(dmm_res)
            except Exception as e:
                raise Exception(f": {e} Could not get Resistance measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_dmm_frequency(self):
        """
        This function measures the internal DMM Frequency
        :return float: DMM Frequency in Hertz
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_frequency = self.daq.query(f'MEAS:FREQ?')
                logging.info(f": Frequency measurement for the internal DMM: {dmm_frequency} Hz")
                return float(dmm_frequency)
            except Exception as e:
                raise Exception(f": {e} Could not get Frequency measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_dmm_period(self):
        """
        This function measures the internal DMM Period
        :return float: DMM Period in ms
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                dmm_period = self.daq.query(f'MEAS:PER?')
                logging.info(f": Period measurement for the internal DMM: {dmm_period} ms")
                return float(dmm_period)
            except Exception as e:
                raise Exception(f": {e} Could not get Period measurement")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_trigger_source(self):
        """
        This query returns the trigger source currently selected.
        :return float: Trigger source - SING| CONT
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                trigger_source = self.daq.query(f'TRIG:SOUR:ALAR?')
                logging.info(f": Checking the trigger source (SING|CONT): {str(trigger_source)}")
                return str(trigger_source)
            except Exception as e:
                raise Exception(f": {e} Could not get Trigger source")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_alarm_condition(self):
        """
        This query returns the condition register for the Alarm Register group.
        :return int: Binary-weighed sum of bits set in alarm register
        """
        system_error = self.daq.query(f'SYST:ERR?')
        if system_error == '+0,"No error"':
            try:
                alarm_condition = self.daq.query(f'STAT:ALAR:COND?')
                logging.info(f": Bits set in Alarm register: {alarm_condition}")
                return alarm_condition
            except Exception as e:
                raise Exception(f": {e} Could not get Alarm Condition")
        else:
            raise Exception(f": SYSTEM ERROR: {system_error} \n")

    def get_1wire_measurements(self, channel_in):
        """
        This function configures the instrument to do voltage, resistance, frequency and period measurements by
        internally triggering the instrument to scan channel n on the module in slot m.
        """
        # TODO check first with sys err
        # TODO break up - Voltage (1 ch and multiple channel) + Freq Res Period

        module_in_use = [k for k, v in self.card_types.items() if v == '34925A-1W']
        slot_in_use = int(KeySight34925A_1W(module_in_use[0]).get_address_by_channel(0))

        meas_dc_volt = self.daq.query(f'MEAS:VOLT:DC? (@{slot_in_use + channel_in})')
        logging.info(f"DC Voltage measurement on channels {slot_in_use + channel_in}: {meas_dc_volt} V")

        meas_res = self.daq.query(
            f'MEAS:RES? 1000,1,(@{slot_in_use + 3}:{slot_in_use + 8})')  # Arbitrary channel so far
        logging.info(f"Resistance measurement for channels {slot_in_use + 3} to {slot_in_use + 8}: {meas_res} Ohm")

        meas_frequency = self.daq.query(
            f'MEAS:FREQ? 100,(@{slot_in_use + 3}, {slot_in_use + 8})')  # Arbitrary channel so far
        logging.info(f"Frequency measurement on channels {slot_in_use + 3} and {slot_in_use + 8}: {meas_frequency} Hz")

        meas_period = self.daq.query(f'MEAS:PER? (@{slot_in_use + 3}, {slot_in_use + 8})')  # Arbitrary channel so far
        logging.info(f"Period measurement on channels {slot_in_use + 3} and {slot_in_use + 8}: {meas_period} ms")

        system_error = self.daq.query(f'SYST:ERR?')
        if system_error != '+0,"No error"':
            raise Exception(f"System error: {system_error}")

class KeySight34925A_1W:
    def __init__(self, slot):
        # Pin Channel Map. Key is Channel, Value is PIN
        self.channel_pin_map = {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
            7: 9,
            8: 10,
            9: 13,
            10: 14,
            11: 35,
            12: 36,
            13: 21,
            14: 22,
            15: 41,
            16: 42,
            17: 27,
            18: 28,
            19: 45,
            20: 46,
            21: 19,
            22: 20,
            23: 39,
            24: 40,
            25: 25,
            26: 26,
            27: 11,
            28: 12,
            29: 31,
            30: 32,
            31: 37,
            32: 38,
            33: 23,
            34: 24,
            35: 43,
            36: 44,
            37: 29,
            38: 30,
            39: 15,
            40: 16,
            "COM": 8
        }
        # Set-up the inverse map Key is Pin, Value is Channel
        self.pin_channel_map = {}
        for channel, pin in self.channel_pin_map.items():
            self.pin_channel_map[pin] = channel

        self.slot = slot

    def get_address_by_pin(self, pin):
        addr = "0000"
        try:
            addr = str(self.slot) + str(self.pin_channel_map[pin]).zfill(3)
        except Exception as e:
            raise Exception(f"Error {e} in Getting Channel address for pin {pin} on slot {self.slot}")
        return addr

    def get_address_by_channel(self, channel):
        return str(self.slot) + str(channel).zfill(3)
