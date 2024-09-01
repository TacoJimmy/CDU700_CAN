import can

def send_can_message(command):
    bus = can.interface.Bus(channel='can0', bustype='socketcan', bitrate=250000)
    msg = can.Message(arbitration_id=0xC0100, data=command, is_extended_id=True)
    
    try:
        bus.send(msg)
        response = bus.recv(timeout=1.0)  # 设置超时时间为1秒
        if response and response.arbitration_id == 0xC0000:
            print(f"Received message: {response}")
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

def calculate_power():
    voltage = send_can_message([0x60, 0x00])
    current = send_can_message([0x61, 0x00])
    
    if voltage is not None and current is not None:
        power = voltage * current
        print(f"Power: {power} W")
    else:
        print("Failed to read voltage or current.")

if __name__ == "__main__":
    calculate_power()