import can
import time
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore.store import ModbusSequentialDataBlock
from threading import Thread


store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 100))  
context = ModbusServerContext(slaves=store, single=True)

def update_modbus_registers(voltage, current):
    context[0x00].setValues(3, 0, [int(voltage * 10)]) 
    context[0x00].setValues(3, 1, [int(current * 10)])  

def read_can_data():
    bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=250000)
    while True:

        voltage = send_can_message(bus, [0x60, 0x00])

        current = send_can_message(bus, [0x61, 0x00])
        
        if voltage is not None and current is not None:
            update_modbus_registers(voltage, current)
            print(f"Updated Modbus registers with Voltage: {voltage} V, Current: {current} A")
        
        time.sleep(5)  # 每5秒读取一次数据

def send_can_message(bus, command):
    msg = can.Message(arbitration_id=0xC0100, data=command, is_extended_id=True)
    
    try:
        bus.send(msg)
        response = bus.recv(timeout=1.0)
        if response and response.arbitration_id == 0xC0000:
            return parse_data(response.data)
        else:
            print("No valid response received.")
            return None

    except can.CanError as e:
        print(f"Error sending message: {e}")
        return None

def parse_data(data):

    value_raw = data[3] << 8 | data[2]
    value = value_raw / 10.0 
    return value

if __name__ == "__main__":

    can_thread = Thread(target=read_can_data)
    can_thread.daemon = True
    can_thread.start()


    StartTcpServer(context, address=("192.168.0.110", 502))