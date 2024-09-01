from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock

def run_modbus_server():
    # 创建一个Modbus数据存储块
    store = ModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0]*100)  # 100个寄存器，初始值为0
    )

    # 创建服务器上下文
    context = ModbusServerContext(slaves=store, single=True)

    # 启动Modbus TCP服务器，监听所有接口，端口502
    StartTcpServer(context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_modbus_server()
