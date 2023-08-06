import time

import pyvisa
import os
import logging


class TDKLambdaPSU:
    """
    Base class for the TDK Lambda PSU
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)

    def __init__(self, connection_string):
        self.psu = None
        self.connection_string = connection_string
        self.resource_manager = None

    def open_connection(self):
        """
        Opens a TCP/IP connection to connect to the TDK Lambda PSU
        """
        self.resource_manager = pyvisa.ResourceManager()
        self.connection_string = os.getenv("PSU_CONNECTION_STRING", default='TCPIP::192.168.123.200::INSTR')
        try:
            logging.info(f": Opening PSU Resource at {self.connection_string}")
            self.psu = self.resource_manager.open_resource(self.connection_string)
        except Exception as e:
            raise Exception(f": ERROR {e}: Could not open Resource")

    def close_connection(self):
        """
        Closes the TCP/IP connection to the TDK Lambda PSU
        """
        self.resource_manager.close()

    def self_test(self):
        """
        Perform a self-test on the device
        :return: Boolean: Pass or fail
        """
        if not self.psu.query(f'SYST:COMM:LAN:MAC?'):
            assert EnvironmentError(f'ERROR: TDK Lambda PSU not found!')
        else:
            logging.info(f": Module found : TDK Lambda PSU")
        self_test = self.psu.query(f'*TST?')
        logging.info(f": Self-test of PSU: {self_test}")
        if self_test == '0':
            logging.info("Self-test Passed!")
            return True
        else:
            raise Exception(f'ERROR in Self-test: Contact Customer Service at TDK-Lambda')

    def id_number(self):
        """
        This function returns the identification number for the TDK Lambda PSU
        :return: str: Instrument ID
        """
        id_num = self.psu.query('*IDN?')
        logging.info(f": ID number of PSU: {id_num}")
        return str(id_num)

    def system_info(self):
        """
        This function collects information about the PSU and the LAN connection to it.
        :return: Logs with information
        """
        # save_settings = self.psu.query(f'*SAV 0')
        # logging.info(f": Save present PSU settings : {save_settings}")
        # print(f": Save present PSU settings : {save_settings}")

        hostname = self.psu.query(f'SYST:COMM:LAN:HOST?')
        logging.info(f": Hostname of PSU: {hostname}")
        # print(f": Hostname of PSU: {hostname}")

        ip_address = self.psu.query(f'SYST:COMM:LAN:IP?')
        logging.info(f": IP Address of PSU: {ip_address}")
        # print(f": IP Address of PSU: {ip_address}")

        mac_address = self.psu.query(f'SYST:COMM:LAN:MAC?')
        logging.info(f": MAC Address of PSU: {mac_address}")
        # print(f": MAC Address of PSU: {mac_address}")

        # start_led_blink = self.psu.query(f'SYSTem:COMMunicate:LAN:IDLED 1')
        # logging.info(f": Start blinking the LED of PSU for 3 secs {start_led_blink}")
        # time.sleep(3)
        # stop_led_blink = self.psu.query(f'SYSTem:COMMunicate:LAN:IDLED 0')
        # logging.info(f": Stop blinking the LED of PSU {stop_led_blink}")

        scpi_version = self.psu.query(f'SYST:VERS?')
        logging.info(f": SCPI version of PSU: {scpi_version}")
        # print(f": SCPI version of PSU: {scpi_version}")

        date = self.psu.query(f'SYST:DATE?')
        logging.info(f": Date: {date}")
        # print(f": Date: {date}")

    def toggle_device_output(self, state):
        """
        This function toggles the PSU output setting - 0|1, OFF|ON - Output state of the PSU
        :param state:
        """
        states = {'0': 'OFF', '1': 'ON'}
        check_state = self.psu.query(f'OUTP:STAT?')
        if check_state != str(state):
            self.psu.query(f'OUTP:STAT {int(state)}')
            time.sleep(0.5)
            if self.psu.query(f'OUTP:STAT?') == '1' and str(state) == '1':
                logging.info(f": PSU Output turned : ON")
                time.sleep(2)
                return True
            elif self.psu.query(f'OUTP:STAT?') == '1' and str(state) != '1':
                logging.error(f"ERROR: Could not toggle output")
                return False
            elif self.psu.query(f'OUTP:STAT?') == '0' and str(state) == '0':
                logging.info(f": PSU Output turned : OFF")
                time.sleep(2)
                return True
            elif self.psu.query(f'OUTP:STAT?') == '0' and str(state) != '0':
                logging.error(f"ERROR: Could not toggle output")
                return False
            else:
                logging.error(f"ERROR: Check the input state for PSU")
                return False
        else:
            logging.info(f": PSU Output is already: {states[str(state)]}")
            return True

    def toggle_display_window(self, disp_state):
        """
        Enables/disables and checks the state of the display window
        :param disp_state: OFF|ON for Boolean values 0|1
        :return:
        """
        query_display_state = self.psu.query(f'DISP:WIND:STAT?')
        logging.info(f": Display window state of PSU: {query_display_state}")

        if query_display_state != disp_state:
            self.psu.query(f'DISP:WIND:STAT {disp_state}')

    def check_min_max_volt(self):
        """
        Checks the min and max programmable voltage level
        :return: tuple: Maximum and Minimum programmable voltage, respectively
        """
        min_volt = self.psu.query(f':VOLT? MIN')
        logging.info(f": Minimum programmable voltage : {min_volt} Volts")
        # print(f": Minimum programmable voltage : {min_volt} Volts")
        max_volt = self.psu.query(f':VOLT? MAX')
        logging.info(f": Maximum programmable voltage : {max_volt} Volts")
        # print(f": Maximum programmable voltage : {max_volt} Volts")
        return float(min_volt), float(max_volt)

    def check_min_max_current(self):
        """
        Checks the min and max programmable current level
        :return: tuple: Maximum and Minimum programmable current, respectively
        """
        min_curr = self.psu.query(f':CURR? MIN')
        logging.info(f": Minimum programmable Current : {min_curr} Amps")
        # print(f": Minimum programmable Current : {min_curr} Amps")

        max_curr = self.psu.query(f':CURR? MAX')
        logging.info(f": Maximum programmable Current : {max_curr} Amps")
        # print(f": Maximum programmable Current : {max_curr} Amps")
        return float(min_curr), float(max_curr)

    def set_output_voltage(self, volt_in):
        """
        This function sets a digital programming output voltage value
        :param volt_in: Voltage in the range of 0-36 Volts
        :return: True or raises Error
        """
        # Enables PSU output setting
        if self.psu.query(f'OUTP:STAT?') == '0':
            self.psu.query(f'OUTP:STAT 1')
        try:
            self.psu.query(f':VOLT {volt_in}')
            voltage = self.get_output_voltage()
            if voltage is not None:
                logging.info(f": Program Output Voltage Set to : {voltage} Volts")
                return True
            else:
                logging.error(f"ERR: Could not set voltage")
                return False
        except Exception as e:
            raise Exception(f"FAIL: to set Voltage : {e}")

    def get_output_voltage(self):
        """
        This function returns the present programmed output voltage
        :return: float: Programmed output voltage in Volts
                 str  : System Error code
        """
        if self.psu.query(f'SYST:ERR?') == '0,"No error"':
            get_volt = self.psu.query(f':VOLT?')
            logging.info(f": Present programmed Output Voltage: {get_volt} Volts")
            return float(get_volt)
        else:
            logging.info(f": System Errors: {self.psu.query(f'SYST:ERR?')}")
            return str(self.psu.query(f'SYST:ERR?'))

    def set_output_current(self, curr_in):
        """
        This function sets a digital programming output current value
        :param curr_in: Current in the range of 0-6 Amps
        :return: True or raises Error
        """
        # Start the PSU
        if self.psu.query(f'OUTP:STAT?') == '0':
            self.psu.query(f'OUTP:STAT 1')
        try:
            self.psu.query(f':CURR {curr_in}')
            current = self.get_output_current()
            if current is not None:
                logging.info(f": Program Output Current Set to : {current} Amps")
                return True
            else:
                logging.error(f"ERR: Could not set current")
                return False
        except Exception as e:
            raise Exception(f"FAIL: to set Current : {e}")

    def get_output_current(self):
        """
        This function returns the present programmed output current
        :return: float: Programmed output voltage in Volts
                 str  : System Error code
        """
        is_system_errors = self.psu.query(f'SYST:ERR?')
        if is_system_errors == '0,"No error"':
            get_current = self.psu.query(f':CURR?')
            logging.info(f": Present programmed Output Current: {get_current} Amps")
            # print(f": Present programmed Output Current: {get_current} Amps")
            return float(get_current)
        else:
            logging.info(f": System Errors: {is_system_errors}")
            return str(is_system_errors)

    def measure_output_voltage(self):
        """
        This function returns a measured output voltage
        :return: float: Output voltage in volts
                 str  : System Error code
        """
        is_system_errors = self.psu.query(f'SYST:ERR?')
        if is_system_errors == '0,"No error"':
            meas_volt = self.psu.query(f'MEAS:VOLT?')
            logging.info(f": Measured Output Voltage: {meas_volt} Volts")
            # print(f": Measured Output Voltage: {meas_volt} Volts")
            return float(meas_volt)
        else:
            logging.info(f": System Errors: {is_system_errors}")
            return str(is_system_errors)

    def measure_output_current(self):
        """
        This function returns a measured output current
        :return: float: Output current in Amps
                 str  : System Error code
        """
        is_system_errors = self.psu.query(f'SYST:ERR?')
        if is_system_errors == '0,"No error"':
            meas_curr = self.psu.query(f'MEAS:CURR?')
            logging.info(f": Measured Output Current: {meas_curr} Amps")
            # print(f": Measured Output Current: {meas_curr} Amps")
            return float(meas_curr)
        else:
            logging.info(f": System Errors: {is_system_errors}")
            return str(is_system_errors)

    def measure_output_power(self):
        """
        This function returns a measured output power
        :return: float: Output Power in Watts
                 str  : System Error code
        """
        is_system_errors = self.psu.query(f'SYST:ERR?')
        if is_system_errors == '0,"No error"':
            meas_pow = self.psu.query(f'MEAS:POW?')
            logging.info(f": Measured Output Power: {meas_pow} Watts")
            # print(f": Measured Output Power: {meas_pow} Watts")
            return float(meas_pow)
        else:
            logging.info(f": System Errors: {is_system_errors}")
            return str(is_system_errors)

    def configuring_output(self):
        """
        This function checks and sets the current & voltage measurements and communication modes with the PSU
        :return:
        """
        is_system_errors = self.psu.query(f'SYST:ERR?')
        logging.info(f": System Errors of PSU: {is_system_errors}")

        operation_mode = self.psu.query(f'SYST:SET?')
        if operation_mode != 'REM':
            set_remote_mode = self.psu.query(f'SYST:SET REM')
            logging.info(f": PSU Operation set to REMOTE Mode {set_remote_mode}")
        meas_voltage = self.psu.query(f'MEAS:VOLT?')
        logging.info(f": Present Voltage of PSU: {meas_voltage}")

        meas_current = self.psu.query(f'MEAS:CURR?')
        logging.info(f": Present Current of PSU: {meas_current}")

        source_mode = self.psu.query(f'SOUR:MOD?')
        logging.info(f": Check CC or CV Mode: {source_mode}")

    def output_protection(self):
        """
        This function checks and sets the voltage and current - output protection limits.
        :return:
        """
        # Checking if there is an OVP fault trip that occurred
        ovp_fault = self.psu.query(f'VOLT:PROT:TRIP?')
        if ovp_fault is not None:
            # to clear the fault and PSU output can be turned on again
            self.psu.query(f'OUTP:STAT ON')

        check_ovp_limit = self.psu.query(f'VOLT:PROT:LEV?')
        logging.info(f": Check Over Voltage Protect Limit: {check_ovp_limit}")

        set_ovp_limit = self.psu.query(f':VOLT:PROT:LEV MAX')  # Arbitrarily set to MAX, could be another value
        logging.info(f": Set Over Voltage Protect Limit to MAX: {set_ovp_limit}")

        get_uvp_limit = self.psu.query(f'VOLT:LIM:LOW?')
        logging.info(f": Check Under Voltage Protect Limit: {get_uvp_limit}")

        set_uvp_limit = self.psu.query(f'VOLT:LIM:LOW 1.1')  # Arbitrary value as yet
        logging.info(f": Set Under Voltage Protect Limit to 1.1 Volts: {set_uvp_limit}")

        # Check if there is a Foldback Protection Trip that occurred
        check_fb_prot_trip = self.psu.query(f'CURR:PROT:TRIP?')
        if check_fb_prot_trip is not None:
            # to clear the fault and PSU output can be turned on again
            self.psu.query(f'OUTP:STAT ON')
            logging.info(f": Resetting PSU after fault trip!")

        check_foldback_protection = self.psu.query(f'CURR:PROT:STAT?')
        if check_foldback_protection is None:
            foldback_protection = self.psu.query(f'CURR:PROT:STAT ON')  # Does not work for CC mode
            logging.info(f": Switching on Foldback Protection if not already on: {foldback_protection}")

        # factory default hostname and description, also closes open lan comm ports
        # reset_lan_comm = self.psu.query(f'DIAG:COMM:LAN:FAC')

        recall_settings = self.psu.query(f'*RCL 0')
        logging.info(f": Recall saved PSU settings : {recall_settings}")
