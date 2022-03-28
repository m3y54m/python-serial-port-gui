import serial

serialPort = serial.Serial(port="COM1", baudrate=9600)

while True:
        # Read only one byte from serial port
        serialPortByte = serialPort.read(1)

        try:
            # Convert byte to string (character)
            char = serialPortByte.decode("ascii")
        except UnicodeDecodeError:
            # Don't raise error if byte is not ASCII
            pass
        else:
            # Print the received byte in Python terminal
            print(char, end="")
