import can

def send_can_message():
    # 配置 CAN 总线
    bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=250000)
    
    # 创建一个 CAN 消息
    msg = can.Message(arbitration_id=0xC0100, data=[0x61, 0x00], is_extended_id=True)
    
    try:
        # 发送消息
        bus.send(msg)
        print(f"Message sent on {bus.channel_info}")

        # 等待并接收响应
        response = bus.recv(timeout=1.0)  # 设置超时时间为1秒
        if response:
            print(f"Received message: {response}")

            # 检查响应消息的 ID
            if response.arbitration_id == 0xC0000:
                # 解析并显示电压值
                voltage = parse_voltage(response.data)
                print(f"Device Voltage: {voltage} V")
            else:
                print(f"Unexpected message ID: {response.arbitration_id}")
        else:
            print("No response received.")

    except can.CanError as e:
        print(f"Error sending message: {e}")

def parse_voltage(data):
    # 根据设备协议解析电压数据
    # 假设电压数据在 data 数组的前两字节
    voltage_raw = data[0] << 8 | data[1]
    voltage = voltage_raw / 100.0  # 假设电压单位是0.01V
    return voltage

if __name__ == "__main__":
    send_can_message()
