# GUI design
import tkinter as tk
from tkinter import scrolledtext

# Communication with serial port
import serial
from serial.tools import list_ports

# Multi-threading
import threading

# Get path
import os

# Use realpath if you want the real path (symlinks are resolved)
# file_path = os.path.realpath(__file__)
FILE_PATH = os.path.abspath(__file__)
ICON_PATH = os.path.join(os.path.dirname(__file__), "icon.png")


class GUI:
    # GUI main class
    def __init__(self, title):

        self.portNamesList = []
        self.baudRatesList = [
            1200,
            2400,
            4800,
            9600,
            19200,
            38400,
            57600,
            115200,
            230400,
            460800,
            576000,
            921600,
        ]
        self.isAnyPortAvailable = False
        self.isStarted = False
        self.serialPortName = None
        self.serialPortBaud = 9600

        self.serialPortManager = SerialPortManager(self.serialPortBaud)
        self.get_available_serial_ports()

        self.guiUpdateInterval = 40

        self.window = tk.Tk()
        # Title of application window
        self.window.title(title)
        # Icon of application window
        self.window.iconphoto(False, tk.PhotoImage(file=ICON_PATH))

        self.topFrame = tk.Frame(self.window, bg="#cccccc")

        self.scanButton = tk.Button(
            self.topFrame,
            text="Scan Serial Ports",
            bg="#0051ff",
            fg="#ffffff",
            border=0,
            highlightbackground="#ffffff",
            highlightthickness=2,
            activebackground="#1f7cff",
            activeforeground="#ffffff",
            font=("Sans", "10", "bold"),
            command=self.scan_button_command,
        )

        # Define a tk.StringVar for storing selected item in OptionMenu
        self.selectedPort = tk.StringVar()
        # Set default value of selectedPort
        if self.isAnyPortAvailable == False:
            self.portNamesList = ["No ports available"]
        self.selectedPort.set(self.portNamesList[0])

        self.portsOptionMenu = tk.OptionMenu(
            self.topFrame, self.selectedPort, *self.portNamesList
        )

        self.portsOptionMenu.configure(
            bg="#ffffff",
            fg="#222222",
            border=0,
            highlightbackground="#aaaaaa",
            activebackground="#eeeeee",
            activeforeground="#111111",
            direction="left",
            font=("Sans", "10", "bold"),
        )
        if self.isAnyPortAvailable == False:
            self.portsOptionMenu.configure(state="disabled")

        # Define a tk.IntVar for storing selected item in OptionMenu
        self.selectedBaudRate = tk.IntVar()
        # Set default value of selectedBaudRate
        self.selectedBaudRate.set(self.baudRatesList[3])
        self.baudRatesOptionMenu = tk.OptionMenu(
            self.topFrame, self.selectedBaudRate, *self.baudRatesList
        )

        self.baudRatesOptionMenu.configure(
            bg="#ffffff",
            fg="#222222",
            border=0,
            highlightbackground="#aaaaaa",
            activebackground="#eeeeee",
            activeforeground="#111111",
            direction="left",
            font=("Sans", "10", "bold"),
        )
        if self.isAnyPortAvailable == False:
            self.baudRatesOptionMenu.configure(state="disabled")

        self.connectButton = tk.Button(
            self.topFrame,
            text="Connect",
            bg="#00a832",
            fg="#ffffff",
            border=0,
            highlightbackground="#ffffff",
            highlightthickness=2,
            activebackground="#3fcc69",
            activeforeground="#ffffff",
            font=("Sans", "10", "bold"),
            command=self.start_button_command,
        )
        if self.isAnyPortAvailable == False:
            self.connectButton.configure(
                state="disabled", bg="#bbbbbb", highlightbackground="#aaaaaa"
            )

        self.textBox = scrolledtext.ScrolledText(
            self.topFrame,
            bg="#222222",
            fg="#eeeeee",
            border=0,
            wrap="none",
            highlightbackground="#aaaaaa",
            highlightthickness=2,
            font=("Sans", "10", "bold"),
        )

        # Start updating textbox in GUI
        self.recursive_update_textbox()

        ###############################
        ## Widgets size and position ##
        ###############################

        spacing = 10
        padding = 10
        widget_width = 800
        window_width = widget_width + 2 * padding
        window_height = 500

        # Size of application window
        self.window.geometry("{}x{}".format(window_width, window_height))
        # Don't allow resizing in the x or y direction
        self.window.resizable(False, False)

        self.topFrame.configure(padx=padding, pady=padding)
        self.topFrame.place(x=0, y=0, width=window_width, height=window_height)

        self.scanButton.configure(width=widget_width, padx=padding, pady=padding)
        self.scanButton.pack(pady=(0, spacing))

        self.portsOptionMenu.configure(width=widget_width, padx=padding, pady=padding)
        self.portsOptionMenu.pack(pady=(0, spacing))

        self.baudRatesOptionMenu.configure(width=widget_width, padx=padding, pady=padding)
        self.baudRatesOptionMenu.pack(pady=(0, spacing))

        self.connectButton.configure(width=widget_width, padx=padding, pady=padding)
        self.connectButton.pack(pady=(0, spacing))

        self.textBox.configure(width=widget_width, padx=padding, pady=padding)
        self.textBox.pack()

        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        # Blocking loop for GUI (Always put at the end)
        self.window.mainloop()

    def start_button_command(self):

        if self.isStarted == False:
            self.isStarted = True
            self.connectButton.configure(
                bg="#ba0020",
                highlightbackground="#ffffff",
                activebackground="#cf324d",
                text="Disconnect",
            )
            # Get desired serial port name
            self.serialPortName = self.selectedPort.get()
            # Get desired serial port baud rate
            self.serialPortBaud = self.selectedBaudRate.get()
            # Start Serial Port Communication
            self.serialPortManager.set_name(self.serialPortName)
            self.serialPortManager.set_baud(self.serialPortBaud)
            self.serialPortManager.start()
            # Start updating textbox in GUI
            self.recursive_update_textbox()

        else:
            self.isStarted = False
            self.connectButton.configure(
                bg="#00a832",
                highlightbackground="#ffffff",
                activebackground="#3fcc69",
                text="Connect",
            )
            self.serialPortManager.stop()

    def scan_button_command(self):
        self.portNamesList = self.get_available_serial_ports()

        if len(self.portNamesList) == 0:
            self.isAnyPortAvailable = False
            self.portNamesList = ["No ports available"]
            self.portsOptionMenu.configure(state="disabled")
            self.baudRatesOptionMenu.configure(state="disabled")
            self.connectButton.configure(
                state="disabled", bg="#bbbbbb", highlightbackground="#aaaaaa"
            )
        else:
            self.isAnyPortAvailable = True
            self.portsOptionMenu.configure(state="normal")
            self.baudRatesOptionMenu.configure(state="normal")
            if self.isStarted:
                self.connectButton.configure(
                    bg="#ba0020",
                    highlightbackground="#ffffff",
                    activebackground="#cf324d",
                    state="normal",
                )
            else:
                self.connectButton.configure(
                    bg="#00a832",
                    highlightbackground="#ffffff",
                    activebackground="#3fcc69",
                    state="normal",
                )

        self.update_option_menu(self.portNamesList)

    def get_available_serial_ports(self):
        # Clear portNames list
        portNames = []
        # Get a list of available serial ports
        portsList = list_ports.comports()
        # Sort based on port names
        portsList = sorted(portsList)

        for port in portsList:
            portNames.append(port.device)

        return portNames

    def update_option_menu(self, portNames):
        # Remove old items
        self.portsOptionMenu["menu"].delete(0, "end")
        # Add new items
        for portName in portNames:
            self.portsOptionMenu["menu"].add_command(
                label=portName, command=tk._setit(self.selectedPort, portName)
            )
        # Set default value of selectedPort
        self.selectedPort.set(portNames[0])

    def recursive_update_textbox(self):
        serialPortBuffer = self.serialPortManager.read_buffer()
        # Update textbox in a kind of recursive function using Tkinter after() method
        self.textBox.insert(tk.INSERT, serialPortBuffer.decode("ascii"))
        # autoscroll to the bottom
        self.textBox.see(tk.END)
        # Recursively call recursive_update_textbox using Tkinter after() method
        if self.serialPortManager.isRunning:
            self.window.after(self.guiUpdateInterval, self.recursive_update_textbox)

    def close_window(self):
        if self.isStarted:
            self.serialPortManager.stop()
        self.window.destroy()


class SerialPortManager:
    # A class for management of serial port data in a separate thread
    def __init__(self, serialPortBaud=9600):
        self.isRunning = False
        self.serialPortName = None
        self.serialPortBaud = serialPortBaud
        self.serialPort = serial.Serial()
        # Create a byte array to store incoming data
        self.serialPortBuffer = bytearray()

    def set_name(self, serialPortName):
        self.serialPortName = serialPortName

    def set_baud(self, serialPortBaud):
        self.serialPortBaud = serialPortBaud

    def start(self):
        self.isRunning = True
        self.serialPortThread = threading.Thread(target=self.thread_handler)
        self.serialPortThread.start()

    def stop(self):
        self.isRunning = False

    def thread_handler(self):

        while self.isRunning:

            if not self.serialPort.isOpen():

                self.serialPort = serial.Serial(
                    port=self.serialPortName,
                    baudrate=self.serialPortBaud,
                    bytesize=8,
                    timeout=2,
                    stopbits=serial.STOPBITS_ONE,
                )
            else:
                # Wait until there is data waiting in the serial buffer
                while self.serialPort.in_waiting > 0:
                    # Read only one byte from serial port
                    serialPortByte = self.serialPort.read(1)
                    self.serialPortBuffer.append(int.from_bytes(serialPortByte, byteorder='big'))
                    # Process incoming bytes
                    self.main_process(serialPortByte)

        if self.serialPort.isOpen():
            self.serialPort.close()

    def read_buffer(self):
        # Return a copy of serial port buffer
        buffer = self.serialPortBuffer
        # Clear serial port buffer
        self.serialPortBuffer = bytearray()
        return buffer

    def __del__(self):
        if self.serialPort.isOpen():
            self.serialPort.close()

    def main_process(self, inputByte):
        # Print the received byte in Python terminal
        try:
            character = inputByte.decode("ascii")
        except UnicodeDecodeError:
            pass
        else:
            print(character, end="")


if __name__ == "__main__":

    # Create the GUI
    gui = GUI("Serial Port + Tkinter GUI")
