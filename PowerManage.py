import can
import time
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import threading

def read_can_voltage(bus, store):
    while True:
        try:
            # 发送读取电压的CAN消息
            msg = can.Message(arbitration_id=0xC0100, data=[0x60, 0x00], is_extended_id=True)
            bus.send(msg)
            
            # 接收响应
            response = bus.recv(timeout=1.0)
            if response and response.arbitration_id == 0xC0000:
                voltage = parse_voltage(response.data)
                print(f"Voltage read from CANBus: {voltage} V")
                
                # 将电压值写入Modbus寄存器地址1（Modbus寄存器是从1开始编号）
                store.set_values(3, 1, [voltage])
            else:
                print("No valid CANBus response received.")
        except can.CanError as e:
            print(f"CANBus error: {e}")
        time.sleep(5)  # 每5秒读取一次电压

def parse_voltage(data):
    # 解析电压值，假设电压数据在data数组的前两字节
    voltage_raw = data[3] << 8 | data[2]
    voltage = voltage_raw / 10.0 
    return voltage

def run_modbus_server():
    # 创建一个Modbus数据存储块，初始值设为10
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [10]*100)  # 100个寄存器，初始值为10
    )

    context = ModbusServerContext(slaves=store, single=True)

    # 启动CANBus监听线程
    can_bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=250000)
    can_thread = threading.Thread(target=read_can_voltage, args=(can_bus, store), daemon=True)
    can_thread.start()

    # 启动Modbus TCP服务器
    StartTcpServer(context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_modbus_server()