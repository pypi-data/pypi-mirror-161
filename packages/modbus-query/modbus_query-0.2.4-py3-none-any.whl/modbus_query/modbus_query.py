import shutil
import yaml
import minimalmodbus
import time
import sys
import os
import datetime
import platformdirs
from threading import Timer

global dataDirectory
global logFileName
global dataFileName
global regMaskRecords
global startDateTime
global cfg
global slave

# Creates a repeated threading timer
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

# Prints a message and writes it to the log file
def printLog(message):
    global dataDirectory
    global logFileName

    if (message != ''):
        if cfg['print_terminal']:
            print(message)
        if cfg['print_log']:
            logFile = open(os.path.join(dataDirectory, logFileName), 'a')
            original_stdout = sys.stdout
            sys.stdout = logFile
            print(message)
            sys.stdout = original_stdout
            logFile.close()

# Adds a timestamp and list of values to the CSV file
def writeCSV(timestamp, value_list):
    global dataDirectory
    global dataFileName

    if cfg['csv_file']:
        dataFile = open(os.path.join(dataDirectory, dataFileName), 'a')
        headerLine = timestamp
        for value in value_list:
            headerLine += ',' + value
            
        headerLine += '\n'
        dataFile.write(headerLine)
        dataFile.close()

# Creates an empty list with a value placed at a specific index for storing to the CSV file
def createList(mask_idx, mask_val):
    value_list = []
    for idx in range(len(cfg['register_masks'])):
        if idx == mask_idx:
            value_list.append(str(mask_val))
        else:
            value_list.append('')
    return value_list

# Reads a register, performs checks, prints related values, and writes them to the CSV file
def read_registers(reg_addr):
    global regMaskRecords
    global startDateTime
    global slave

    # Read the register
    try:
        val = int(slave.read_register(reg_addr))
    except IOError as e:
        # printLog('Error: Failed to read register address ' + '{0:#0{1}x}'.format(reg_addr, 6) + ': ' + e.args[0])
        return

    # Find all register masks with a matching address
    for idx, mask_cfg in enumerate(cfg['register_masks']):
        if mask_cfg['address'] == reg_addr:
            # If the mask is 0, skip it
            if mask_cfg['mask'] == 0:
                printLog('Error: Register mask was 0 for prefix \"' + mask_cfg['prefix'] + '\"')
                continue

            # AND the register value with the register mask
            val &= mask_cfg['mask']
            # Shift the register value and its mask until the mask has its first bit set to 1
            temp = mask_cfg['mask']
            while not (temp & 0x1):
                val >>= 1
                temp >>= 1

            val = float(val) / (10 ** mask_cfg['decimals'])

            # Perform min/max value functionality
            if mask_cfg['function'] == 'min':
                if val < mask_cfg['reset_thld']:
                    val = min(val, regMaskRecords[idx][0])
            elif mask_cfg['function'] == 'max':
                if val > mask_cfg['reset_thld']:
                    val = max(val, regMaskRecords[idx][0])
            elif mask_cfg['function'] == 'average':
                regMaskRecords[idx][1] += 1
                val = regMaskRecords[idx][0] + (val / regMaskRecords[idx][1])

            # Set the mask records to the current values
            regMaskRecords[idx][0] = val

            # Convert to float with X decimals
            formatted_val = format(val, '.' + str(mask_cfg['decimals']) + 'f')
            int_timestamp = format(round(datetime.datetime.now().timestamp() - startDateTime), '010d')
            float_timestamp = format(datetime.datetime.now().timestamp() - startDateTime, '.3f')
            # Print the value with or without a timestamp
            if cfg['print_timestamp']:
                printLog('[' + int_timestamp + '] ' + mask_cfg['prefix'] + ': ' + formatted_val)
            else:
                printLog(mask_cfg['prefix'] + ': ' + formatted_val)

            # Write the value to the CSV file
            writeCSV(float_timestamp, createList(idx, formatted_val))

def main():
    global dataDirectory
    global logFileName
    global dataFileName
    global regMaskRecords
    global startDateTime
    global cfg
    global slave

    # Create start time
    startDateTime = datetime.datetime.now().timestamp()

    # Create the user data folder
    userDirectory = os.path.join(platformdirs.user_data_dir(), 'ModbusQuery')
    if not os.path.exists(userDirectory):
        os.mkdir(userDirectory)
    
    # Copy the default configuration to the user data folder
    if not os.path.exists(os.path.join(userDirectory, 'config.yaml')):
        shutil.copyfile(os.path.join(os.path.abspath( os.path.dirname(__file__)),'config.yaml'), os.path.join(userDirectory, 'config.yaml'))

    # Load the configuration
    with open(os.path.join(userDirectory, 'config.yaml'), 'r') as file:
        cfg = yaml.safe_load(file)

    # Create the app's data directory in the user data folder if it doesn't already exist
    dataDirectory = os.path.join(userDirectory, 'Data')
    if not os.path.exists(dataDirectory):
        os.mkdir(dataDirectory)

    # Create file names
    logFileName = 'modbus_query' + '_' + time.strftime('%Y%m%d-%H%M%S') + '.log'
    dataFileName = 'modbus_query' + '_' + time.strftime('%Y%m%d-%H%M%S') + '.csv'

    # Fill the register mask records with empty data
    regMaskRecords = [[0 for x in range(2)] for y in range(len(cfg['register_masks']))]

    csv = []

    # Add the register mask prefixes to the CSV
    for mask_cfg in cfg['register_masks']:
        csv.append(mask_cfg['prefix'])

    writeCSV('Time (s)', csv)
    printLog('User data directory path: ' + userDirectory)

    # Configure the Modbus settings
    slave = minimalmodbus.Instrument(cfg['serial_port'], cfg['slave_address'])
    slave.serial.baudrate = cfg['serial_baud']
    slave.serial.timeout = float(cfg['query_timeout']) / 1000

    printLog('Connected to port: ' + cfg['serial_port'])

    printLog('Scheduling register reads...')

    # Schedule each Modbus register read with delays based on configuration
    for reg_cfg in cfg['registers']:
        RepeatTimer(float(reg_cfg['period']) / 1000, read_registers, [reg_cfg['address']]).start()

    while 1:
        pass

    printLog('Error, exited scheduler loop...')

if __name__ == '__main__':
    main()
