import time
import logging

import serial
from serial.tools import list_ports

COMMON_TEST_MODE = ["AC", "DC", "IR"]
CHANNEL_VALUE = ["HIGH", "LOW", "OPEN"]


class HipotTester:
    """
    Base class for the Sourcetronic ST9201 Hipot Tester
    """
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    def __init__(self, connection_string):
        self.tic = None
        self.toc = None
        self.ser = None
        self.hipot_tester = None
        self.port = None
        self.connection_string = connection_string

    def open_connection(self):
        """
        Opens a serial connection with the Hipot tester
        :return:
        """
        self.port = list(list_ports.comports())
        # self.hipot_tester = [str(p.device) for p in self.port if str(p).startswith("/dev/cu.usbserial")]
        self.ser = serial.Serial(self.connection_string, baudrate=19200, stopbits=serial.STOPBITS_TWO, timeout=1)
        self.tic = time.perf_counter()
        logging.info(f"Opening serial connection to port {self.ser} ...")
        # print("Opening serial connection...")

    def close_connection(self):
        """
        Closes a serial connection with the Hipot tester
        :return:
        """
        self.ser.close()
        self.toc = time.perf_counter()
        logging.info(f"Testing time: {self.toc - self.tic:0.4f} seconds ! ")
        logging.info(f"Closing serial connection")
        # print(f"Closing serial connection")

    def id_number(self):
        """
        This function returns the ID number
        :return: str: IDN
        """
        idn = "*IDN? \r \n"
        self.ser.write(idn.encode())
        read_char = self.ser.read(20).decode()
        logging.info(f":IDN: {read_char}")
        return str(read_char)

    def system_info(self):
        """
        Gathers system info about the serial interface
        :return:
        """
        sys_version = ":SYST:VERS? \r \n"
        self.ser.write(sys_version.encode())
        read_char = self.ser.read(20).decode()
        logging.info(f": SYSTEM VERSION: {read_char}")
        # print(f": SYSTEM VERSION: {read_char}")

        fetch = ":SYST:FETCH? \r \n"
        self.ser.write(fetch.encode())
        read_char = self.ser.read(20).decode()
        logging.info(f": SYSTEM FETCH: {read_char}")
        # print(f": SYSTEM FETCH: {read_char}")

        sys_time_pass = ":SYST:TIME:PASS? \r \n"
        self.ser.write(sys_time_pass.encode())
        read_char = self.ser.read(20).decode()
        logging.info(f": SYSTEM TIME PASS: {read_char}")
        # print(f": SYSTEM TIME PASS: {read_char}")

        sys_range = ":SYST:WRAN? \r \n"
        self.ser.write(sys_range.encode())
        read_char = self.ser.read(20).decode()
        logging.info(f": SYSTEM RANGE: {read_char}")
        # print(f": SYSTEM RANGE: {read_char}")

        sys_lock = ":SYST:LOCK? \r \n"
        self.ser.write(sys_lock.encode())
        read_char = self.ser.read(20).decode()
        logging.info(f": SYSTEM LOCK: {read_char}")
        # print(f": SYSTEM LOCK: {read_char}")

        sys_agc = ":SYST:DAGC? \r \n"
        self.ser.write(sys_agc.encode())
        read_char = self.ser.read(20).decode()
        logging.info(f": SYSTEM AGC: {read_char}")
        # print(f": SYSTEM AGC: {read_char}")

        sys_offset = ":SYST:OFFSET? \r \n"
        self.ser.write(sys_offset.encode())
        read_char = self.ser.read(20).decode()
        logging.info(f": SYSTEM OFFSET: {read_char}")
        # print(f": SYSTEM OFFSET: {read_char}")

        sys_part = ":SYST:PART? \r \n"
        self.ser.write(sys_part.encode())
        read_resp = self.ser.read(20).decode()
        logging.info(f": SYSTEM PART: {read_resp}")
        # print(f": SYSTEM PART: {read_resp}")

        sys_arc = ":SYST:ARC? \r \n"
        self.ser.write(sys_arc.encode())
        read_resp = self.ser.read(20).decode()
        logging.info(f": SYSTEM ARC: {read_resp}")
        # print(f": SYSTEM ARC: {read_resp}")

    # Set and get voltage for ACW/DCW/IR test
    def set_voltage(self, step, test_mode, voltage):
        """
        This function sets the voltage for the ACW/DCW/IR test
        :param step: The step for which the voltage is added in the range 1-49
        :param voltage: The voltage to be set in Volts in range 50-5000 volts for ACW test
                        and it must be set in Volts in range 50-6000 volts for DCW test
        :param test_mode: modes being AC/DC/IR
        """
        # Set voltage for ACW/DCW/IR test
        if str(test_mode).upper() in COMMON_TEST_MODE:
            set_voltage = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:LEV {voltage} \r \n"
            self.ser.write(set_voltage.encode())
            self.ser.read(20).decode()
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def get_voltage(self, step, test_mode):
        """
        This function checks the voltage for the ACW test
        :param step: The step for which the voltage is added in the range 1-49
        :param test_mode: modes being AC/DC/IR
        :return: int: Voltage value in volts
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            get_voltage = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:LEV? \r \n"
            self.ser.write(get_voltage.encode())
            read_char = self.ser.read(20).decode()
            logging.info(f": GET AC VOLTAGE for step 1: {read_char} Volts")
            # print(f": GET AC VOLTAGE for step 1: {read_char} Volts")
            return int(read_char)
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def set_current_limits(self, step, test_mode, low_limit, high_limit):
        """
        This functions sets the lower and upper current limits for ACW/DCW test
        :param test_mode: modes being AC/DC
        :param step: The step for which the current is added in the range 1-49
        :param low_limit: Lower current limit in range 0~30.000E-3 (0 is OFF) Amps for ACW test and
                          lower current limit in range 0~10.000E-3 (0 is OFF) Amps for DCW test
        :param high_limit: Upper current limit in range 1.00E-6~30.000E-3 Amps for ACW test and
                           upper current limit in range 1.00E-6~10.000E-3 Amps for DCW test.
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            set_low_current = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:LIM:LOW {low_limit} \r \n"
            self.ser.write(set_low_current.encode())
            self.ser.read(20).decode()

            set_high_current = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:LIM:HIGH {high_limit} \r \n"
            self.ser.write(set_high_current.encode())
            self.ser.read(20).decode()
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def get_current_limits(self, step, test_mode):
        """
        This function checks the lower and upper current limits set by the user/by default
        :param test_mode: modes being AC/DC/IR
        :param step: The step for which the current is added in the range 1-49
        :return: tuple: Lower and upper current limits in Amps respectively
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            get_low_current = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:LIM:LOW? \r \n"
            self.ser.write(get_low_current.encode())
            read_char_low = self.ser.read(20).decode()
            logging.info(f": GET LOW CURRENT LIMIT for step {step}: {read_char_low} Amps")

            get_high_current = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:LIM:HIGH? \r \n"
            self.ser.write(get_high_current.encode())
            read_char_high = self.ser.read(20).decode()
            logging.info(f": GET HIGH CURRENT LIMIT for step {step}: {read_char_high} Amps")
            return float(read_char_low), float(read_char_high)
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def arc_set_current_limits(self, step, limit, test_mode):
        """
        This functions sets the ARC current limit for ACW/DCW test
        :param step: The step for which the current is added in the range 1-49
        :param limit: Current limit in range 0~15.0E-3 (0 is OFF) Amps for ACW test and
                      current limit in range 0~10.0E-3 (0 is OFF) Amps for DCW test.
        :param test_mode: modes being AC/DC/IR
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            set_arc_current = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:LIM:ARC {limit} \r \n"
            self.ser.write(set_arc_current.encode())
            self.ser.read(20).decode()
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def arc_get_current_limits(self, step, test_mode):
        """
        This functions sets the ARC current limit for ACW/DCW test
        :param step: The step for which the current is added in the range 1-49
        :param test_mode: modes being AC/DC
        :return: float: ARC current limit in Amps
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            set_arc_current = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:LIM:ARC? \r \n"
            self.ser.write(set_arc_current.encode())
            read_char_arc = self.ser.read(20).decode()
            logging.info(f": GET ARC CURRENT LIMIT for step {step}: {read_char_arc} Amps")
            return float(read_char_arc)
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def set_ramp_time(self, step, ramp_time, test_mode):
        """
        This functions sets the RISE time for ACW/DCW/IR tests
        :param step: The step for which the current is added in the range 1-49
        :param ramp_time: Time in range 0~999.9 (0 is OFF) seconds for ACW/DCW/IR test.
        :param test_mode: modes being AC/DC/IR
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            set_ramp = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:TIME:RAMP {ramp_time} \r \n"
            self.ser.write(set_ramp.encode())
            self.ser.read(20).decode()
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def get_ramp_time(self, step, test_mode):
        """
        This functions sets RAMP time for ACW/DCW/IR test
        :param step: The step for which the current is added in the range 1-49
        :param test_mode: modes being AC/DC/IR
        :return: float: Ramp time in seconds
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            get_ramp = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:TIME:RAMP? \r \n"
            self.ser.write(get_ramp.encode())
            read_char_ramp = self.ser.read(20).decode()
            logging.log(f": GET RAMP TIME for step {step}: {read_char_ramp} seconds")
            return float(read_char_ramp)
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def set_fall_time(self, step, fall_time, test_mode):
        """
        This functions sets the FALL time for ACW/DCW/IR tests
        :param step: The step for which the current is added in the range 1-49
        :param fall_time: Time in range 0~999.9 (0 is OFF) seconds for ACW/DCW/IR test.
        :param test_mode: modes being AC/DC/IR
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            set_fall_time = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:TIME:FALL {fall_time} \r \n"
            self.ser.write(set_fall_time.encode())
            self.ser.read(20).decode()
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def get_fall_time(self, step, test_mode):
        """
        This functions sets the FALL time for ACW/DCW/IR test
        :param step: The step for which the current is added in the range 1-49
        :param test_mode: modes being AC/DC/IR
        :return: float: Fall time in seconds
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            get_fall_time = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:TIME:FALL? \r \n"
            self.ser.write(get_fall_time.encode())
            read_char_fall = self.ser.read(20).decode()
            logging.info(f": GET FALL TIME for step {step}: {read_char_fall} seconds")
            return float(read_char_fall)
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def set_test_time(self, step, test_time, test_mode):
        """
        This functions sets the TEST time for ACW/DCW/IR tests
        :param step: The step for which the current is added in the range 1-49
        :param test_time: Time in range 0~999.9 (0 is OFF) seconds for ACW/DCW/IR test
        :param test_mode: modes being AC/DC/IR
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            set_test_time = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:TIME:FALL {test_time} \r \n"
            self.ser.write(set_test_time.encode())
            self.ser.read(20).decode()
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def get_test_time(self, step, test_mode):
        """
        This functions sets the TEST time for the ACW/DCW/IR test
        :param step: The step for which the current is added in the range 1-49
        :param test_mode: modes being AC/DC/IR
        :return: float: TEST time in seconds
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            get_test_time = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:TIME:FALL? \r \n"
            self.ser.write(get_test_time.encode())
            read_char_test = self.ser.read(20).decode()
            logging.info(f": GET TEST TIME for step {step}: {read_char_test} seconds")
            return float(read_char_test)
        else:
            raise OSError(f"ERROR: not the correct Test Mode : {test_mode}")

    def set_channel(self, step, test_mode, channel, chan_value):
        """
        This functions sets HIGH/LOW/OPEN for the scanner channel for ACW/DCW/IR test.
        :param step: The step for which the current is added in the range 1-49
        :param test_mode: modes being AC/DC/IR
        :param channel: Channel in the range of 1-8
        :param chan_value: Channel values being HIGH/LOW/OPEN
        """
        if (str(test_mode).upper() in COMMON_TEST_MODE) and (str(chan_value).upper() in CHANNEL_VALUE):
            set_channel_value = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:CHAN {channel}:{str(chan_value).upper()} \r \n"
            self.ser.write(set_channel_value.encode())
            self.ser.read(20).decode()
        else:
            raise OSError(f"ERROR: not the correct Test Mode: {test_mode} /Channel Value {chan_value}")

    def get_channel(self, step, test_mode, channel):
        """
        This functions inquires about the set channel value for ACW/DCW/IR test.
        :param channel: Channel value set in the range for 1-8
        :param step: The step for which the current is added in the range 1-49
        :param test_mode: modes being AC/DC/IR
        :return: str: Channel value in HIGH/LOW/OPEN
        """
        if str(test_mode).upper() in COMMON_TEST_MODE:
            get_test_time = f":SOUR:SAFE:STEP {step}:{str(test_mode).upper()}:CHAN {channel}? \r \n"
            self.ser.write(get_test_time.encode())
            read_char_chan_value = self.ser.read(20).decode()
            logging.info(f": GET CHANNEL VALUE for step {step} and channel {channel}: {read_char_chan_value}")
            return str(read_char_chan_value)
        else:
            raise OSError(f"ERROR: not the correct Test Mode: {test_mode}")

    def set_ac_freq(self, step, freq):
        """
        This functions sets the test frequency for ACW test
        :param step: The step for which the current is added in the range 1-49
        :param freq: Set value 50/60 Hz in ACW test
        """
        set_test_time = f":SOUR:SAFE:STEP {step}:AC:TIME:FREQ {freq}\r \n"
        self.ser.write(set_test_time.encode())
        self.ser.read(20).decode()

    def get_ac_freq(self, step):
        """
        This functions checks the test frequency for ACW test.
        :param step: The step for which the current is added in the range 1-49
        :return: float: Value for the test FREQUENCY
        """
        get_test_time = f":SOUR:SAFE:STEP {step}:AC:TIME:FREQ? \r \n"
        self.ser.write(get_test_time.encode())
        read_char_ac_freq = self.ser.read(20).decode()
        logging.info(f": GET AC FREQUENCY for step {step}: {read_char_ac_freq} Hz")
        return float(read_char_ac_freq)

    def set_real_current(self, step, real_curr):
        """
        This functions sets the REAL current for ACW test
        :param real_curr: Current in range 0~30.000E-3 (0 is OFF) Amps for ACW test
        :param step: The step for which the current is added in the range 1-49
        """
        set_ac_real_curr = f":SOUR:SAFE:STEP {step}:AC:LIM:REAL {real_curr}\r \n"
        self.ser.write(set_ac_real_curr.encode())
        self.ser.read(20).decode()

    def get_real_current(self, step):
        """
        This functions checks the REAL current for ACW test
        :param step: The step for which the current is added in the range 1-49
        :return: float: Value for the REAL current
        """
        get_test_time = f":SOUR:SAFE:STEP {step}:AC:LIM:REAL? \r \n"
        self.ser.write(get_test_time.encode())
        read_char_real_curr = self.ser.read(20).decode()
        logging.info(f": GET AC REAL CURRENT for step {step}: {read_char_real_curr} Amps")
        return float(read_char_real_curr)

    def set_dc_wait_time(self, step, wait):
        """
        This functions sets the WAIT time for DCW test
        :param wait: Wait time in seconds in range 0~999.9 (0 is OFF) for DCW test
        :param step: The step for which the current is added in the range 1-49
        """
        set_dc_wait = f":SOUR:SAFE:STEP {step}:DC:TIME:DWEL {wait}\r \n"
        self.ser.write(set_dc_wait.encode())
        self.ser.read(20).decode()

    def get_dc_wait_time(self, step):
        """
        This functions checks the WAIT time for DCW test
        :param step: The step for which the current is added in the range 1-49
        :return: float: Value for the WAIT time in seconds
        """
        get_dc_wait = f":SOUR:SAFE:STEP {step}:DC:TIME:DWEL? \r \n"
        self.ser.write(get_dc_wait.encode())
        read_char_wait = self.ser.read(20).decode()
        logging.info(f": GET DC WAIT TIME for step {step}: {read_char_wait} seconds")
        return float(read_char_wait)

    def set_ir_resistance(self, step, low_limit, high_limit):
        """
        This functions sets the lower and upper resistance for IR test
        :param step: The step for which the resistance is added in the range 1-49
        :param low_limit: Lower Resistance in range 1.0E5~5.0E10 Ohms for IR test
        :param high_limit: Upper Resistance in range 0~5E10 (0 is OFF) Ohms for IR test
        """
        set_low_resistance = f":SOUR:SAFE:STEP {step}:IR:LIM:LOW {low_limit} \r \n"
        self.ser.write(set_low_resistance.encode())
        self.ser.read(20).decode()

        set_high_resistance = f":SOUR:SAFE:STEP {step}:IR:LIM:HIGH {high_limit} \r \n"
        self.ser.write(set_high_resistance.encode())
        self.ser.read(20).decode()

    def get_ir_resistance(self, step):
        """
        This function checks the lower and upper resistance set by the user/by default
        :param step: The step for which the resistance is added in the range 1-49
        :return: tuple: Lower and upper resistance limits in Ohms respectively
        """
        get_low_resistance = f":SOUR:SAFE:STEP {step}:IR:LIM:LOW? \r \n"
        self.ser.write(get_low_resistance.encode())
        read_char_low = self.ser.read(20).decode()
        logging.info(f": GET LOW RESISTANCE for step {step}: {read_char_low} Ohms")

        get_high_resistance = f":SOUR:SAFE:STEP {step}:IR:LIM:HIGH? \r \n"
        self.ser.write(get_high_resistance.encode())
        read_char_high = self.ser.read(20).decode()
        logging.info(f": GET HIGH RESISTANCE for step {step}: {read_char_high} Ohms")
        return float(read_char_low), float(read_char_high)


