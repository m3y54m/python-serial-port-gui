import serial

serialPort = serial.Serial(port="COM1", baudrate=9600)

sb = bytearray()
print(sb)
sb.append(1)
sb.append(2)
sb.pop(0)
print(len(sb))
print(sb)
while False:
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
