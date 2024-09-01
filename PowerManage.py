import can
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.transaction import ModbusSocketFramer
import threading

# CANBus 配置和数据读取
def read_can_data():
    bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=250000)
    while True:
        try:
            message = bus.recv(timeout=1.0)
            if message and message.arbitration_id == 0xC0000:
                voltage = parse_data(message.data, 0)
                current = parse_data(message.data, 1)
                # 更新 Modbus 数据
                store.set_values(3, 0, [voltage, current])
            time.sleep(5)
        except Exception as e:
            print(f"Error reading CAN data: {e}")

def parse_data(data, index):
    # 解析数据，假设数据格式为 [高字节, 低字节]
    value_raw = data[index * 2 + 1] << 8 | data[index * 2]
    return value_raw / 10.0

# Modbus TCP 服务器配置
def setup_modbus_server():
    global store
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0] * 10),
        ir=ModbusSequentialDataBlock(0, [0] * 10)
    )
    context = ModbusServerContext(slaves=store, single=True)
    StartTcpServer(context, framer=ModbusSocketFramer, address=("192.168.0.110", 5020))

if __name__ == "__main__":
    # 启动 Modbus 服务器线程
    modbus_thread = threading.Thread(target=setup_modbus_server, daemon=True)
    modbus_thread.start()
    
    # 启动 CAN 数据读取线程
    can_thread = threading.Thread(target=read_can_data, daemon=True)
    can_thread.start()
    
    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped.")