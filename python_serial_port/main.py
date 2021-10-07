import serial

serialPort = serial.Serial(port="/dev/ttyACM0", baudrate=921600,
                           bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)

while(1):
    # Wait until there is data waiting in the serial buffer
    while(serialPort.in_waiting > 0):
        # Read only one byte from serial port
        serialPortByte = serialPort.read(1)
        # Print the received byte in Python terminal
        try:
            serialPortByte.decode("ascii")
        except UnicodeDecodeError:
            pass
        else:
            print(serialPortByte.decode("Ascii"), end="")
