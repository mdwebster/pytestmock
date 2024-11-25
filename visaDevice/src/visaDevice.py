import pyvisa
import threading

class VISADevice():
    """
    class to control visa device
    """
    resourceManager_ = pyvisa.ResourceManager()
    
    def __init__(self):
        self.deviceAddress_ = "127.0.0.1:4567"
        self.deviceLock_ = threading.Lock()
        self.deviceOn_ = False
        self.device_ = self.resourceManager_.open_resource(
            self.deviceAddress_, write_termination="\n", read_termination="\n"
        )
    
    def setup_component(self):
        cmds = {
            "channel 1": {"state": "OFF", "voltage": 0, "current": 0},
            "channel 2": {"state": "OFF", "voltage": 0, "current": 0},
        }
        self.turn_on(cmds)
    
    def teardown_component(self):
        if self.deviceOn_:
            self.turn_off()
        self.device_.close()
        
    def turn_on(self, cmds):
        try:
            with self.deviceLock_:
                self.set_channel(self.device_, 1, "VOLT", cmds["channel 1"]["voltage"])
                self.set_channel(self.device_, 1, "CURR", cmds["channel 1"]["current"])
                self.set_channel_state(self.device_, 1, cmds["channel 1"]["state"])
                self.set_channel(self.device_, 2, "VOLT", cmds["channel 2"]["voltage"])
                self.set_channel(self.device_, 2, "CURR", cmds["channel 2"]["current"])
                self.set_channel_state(self.device_, 2, cmds["channel 2"]["state"])
        except Exception as e:
            print(e)
            raise e
        self.deviceOn_ = True
    
    def turn_off(self):
        try:
            with self.deviceLock_:
                self.set_channel_state(self.device_, 1, "OFF")
                self.set_channel_state(self.device_, 2, "OFF")
        except Exception as e:
            print(e)
            raise e
        self.deviceOn_ = False

    def set_channel(self, device, channel, volt_or_curr, val):
        try:
            device.write(f"{volt_or_curr} {val:4f} , (@{channel})")
        except TypeError as e:
            raise ValueError(e) from e
    
    def set_channel_state(self, device, channel, state):
        try:
            device.write(f"OUTPut {state} , (@{channel})")
        except TypeError as e:
            raise ValueError(e) from e
    
