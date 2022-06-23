import time
import serial
import serial.tools.list_ports


class ZyboSerial:

    def __init__(self,port,baudrate=921600, timeout=1):

        self.zybo = None
        self.zybo_port = self.find_zybo_port(port)

        try:
            self.connect(self.zybo_port,baudrate=baudrate, timeout=1)
        except:
            print("Cannot connect to the Zybo board, please reboot the board and try again")
        else:
            print("Successfully connected to Zybo through port %s"%self.zybo_port)


    def find_zybo_port(self,port=None):
        """Get the name of the port that is connected to Zybo."""
        if port is None:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if p.manufacturer is not None and "FTDI" in p.manufacturer:
                    port = p.device
        return port

    def connect(self,port, baudrate=921600, timeout=1):
        self.zybo = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.zybo.close()
        self.zybo.open()
        time.sleep(1)

    def refresh(self):
        self.zybo.close()
        self.zybo.open()
        time.sleep(1)






