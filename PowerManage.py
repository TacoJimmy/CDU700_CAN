import can
import time
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import threading

# 配置 CANBus 参数
CAN_CHANNEL = 'can0'
CAN_BITRATE = 250000

# 定义每个设备的 CAN 消息 ID 和 Modbus 寄存器地址映射
DEVICE_CAN_IDS = {
    0: 0xC0100,
    1: 0xC0101,
    2: 0xC0102,
    3: 0xC0103
}

MODBUS_REGISTER_BASE = 0
NUM_DEVICES = len(DEVICE_CAN_IDS)

def read_can_data(bus, store):
    while True:
        for device_id, can_id in DEVICE_CAN_IDS.items():
            try:
                # 发送电压消息
                voltage_msg = can.Message(arbitration_id=can_id, data=[0x60, 0x00], is_extended_id=True)
                bus.send(voltage_msg)
                voltage_response = bus.recv(timeout=1.0)
                if voltage_response and voltage_response.arbitration_id == (can_id-0x100):
                    voltage = (voltage_response.data[3] << 8 | voltage_response.data[2]) / 10.0
                    voltage_int = int(voltage * 10)
                    store.setValues(3, MODBUS_REGISTER_BASE + device_id * 2, [voltage_int])  # 电压寄存器地址
                    print(f"Device {device_id} Voltage: {voltage} V")
                else:
                    voltage_int = int(0)
                    store.setValues(3, MODBUS_REGISTER_BASE + device_id * 2, [voltage_int])  # 电压寄存器地址
                    print(f"Device {device_id} Voltage: {0} V")

                # 发送电流消息
                current_msg = can.Message(arbitration_id=can_id, data=[0x61, 0x00], is_extended_id=True)
                bus.send(current_msg)
                current_response = bus.recv(timeout=1.0)
                if current_response and current_response.arbitration_id == (can_id-0x100):
                    current = (current_response.data[3] << 8 | current_response.data[2]) / 10.0
                    current_int = int(current * 10)
                    store.setValues(3, MODBUS_REGISTER_BASE + device_id * 2 + 1, [current_int])  # 电流寄存器地址
                    print(f"Device {device_id} Current: {current} A")
                else:
                    current_int = int(0)
                    store.setValues(3, MODBUS_REGISTER_BASE + device_id * 2 + 1, [current_int])  # 电流寄存器地址
                    print(f"Device {device_id} Current: {0} A")
                    
            except can.CanError as e:
                print(f"CANBus error: {e}")
        
        time.sleep(5)  # 每5秒读取一次数据

def run_modbus_server():
    initial_values = [10] * (NUM_DEVICES * 2)  # 每个设备2个寄存器（电压和电流）
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [10]*10)  # 设定初始值
    )
    context = ModbusServerContext(slaves=store, single=True)
    can_bus = can.interface.Bus(channel=CAN_CHANNEL, bustype='socketcan', bitrate=CAN_BITRATE)
    can_thread = threading.Thread(target=read_can_data, args=(can_bus, store), daemon=True)
    can_thread.start()

    # 启动 Modbus TCP 服务器
    StartTcpServer(context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_modbus_server()