import pytest
from flexmock import flexmock
from visaDevice.src.visaDevice import VISADevice
import regex as re

class TestVisaDevice:
    
    deviceDict_ = {}
    
    class VisaDeviceUUT(VISADevice):
        
        def __init__(self, testClass):
            super().__init__()
            self.error_ = False
            self.testClass_ = testClass
            self.deviceAddress_ = "None"
        
        
    @pytest.fixture
    def device_mock(self):
        deviceMock = flexmock()
        deviceMock.should_receive("query").replace_with(self.query)
        deviceMock.should_receive("write").replace_with(self.write)
        deviceMock.should_receive("close").replace_with(self.close)
        
        flexmock(self.VisaDeviceUUT).should_receive("resourceManager_.open_resource").and_return(deviceMock)
        
        uut = self.VisaDeviceUUT(self)
        yield uut
        uut.teardown_component()
    
    @pytest.mark.parametrize("ch1v, ch1c, ch2v, ch2c", [(0,0,0,0), (5,5,5,5)])
    def test_turn_on(self, device_mock, ch1v, ch1c, ch2v, ch2c):
        cmds = {
            "channel 1": {"state": "ON", "voltage": ch1v, "current": ch1c},
            "channel 2": {"state": "ON", "voltage": ch2v, "current": ch2c},
        }
        device_mock.turn_on(cmds)
        assert self.deviceDict_["ch1v"] == cmds["channel 1"]["voltage"]
        
        
    def close(self):
        assert not self.deviceDict_["ch1_on"]
        assert not self.deviceDict_["ch2_on"]
    
    def write(self,string):
        regex = r"((^VOLT|^CURR) [0-9. ]+, \(@(1|2)\)$|^OUTPut (ON|OFF) , \(@(1|2)\)$)"
        if re.match(regex, string) is None:
            print(f"Write {string}")
            raise ValueError("String didn't pass regex")
        if "CURR" in string:
            if "@1" in string:
                self.deviceDict_["ch1c"] = float(string.split(" ")[1])
            elif "@2" in string:
                self.deviceDict_["ch2c"] = float(string.split(" ")[1])
            else:
                raise ValueError(f"{string}: Didn't parse correctly")
        elif "VOLT" in string:
            if "@1" in string:
                self.deviceDict_["ch1v"] = float(string.split(" ")[1])
            elif "@2" in string:
                self.deviceDict_["ch2v"] = float(string.split(" ")[1])
            else:
                raise ValueError(f"{string}: Didn't parse correctly")
        elif "OUTPut" in string:
            if "ON" in string:
                if "@1" in string:
                    self.deviceDict_["ch1_on"] = True
                elif "@2" in string:
                    self.deviceDict_["ch2_on"] = True
            elif "OFF" in string:
                if "@1" in string:
                    self.deviceDict_["ch1_on"] = False
                    self.deviceDict_["ch1v"] = 0
                    self.deviceDict_["ch1c"] = 0
                elif "@2" in string:
                    self.deviceDict_["ch2_on"] = False
                    self.deviceDict_["ch2v"] = 0
                    self.deviceDict_["ch2c"] = 0
            else:
                raise ValueError(f"{string}: Didn't parse correctly")
        else:
            raise ValueError(f"{string}: Didn't parse correctly")
    
    def query(self, string):
        regex = r"^MEASure:(VOLTage|CURRent)\? \(@(1|2)\)$|^(SYST:ERR\?)$"
        if re.match(regex,string) is None:
            print(f"Query {string}")
            raise ValueError("String didn't pass regex")
        if "CURR" in string:
            if "@1" in string:
                return self.deviceDict_["ch1c"]
            if "@2" in string:
                return self.deviceDict_["ch2c"]
            raise ValueError(f"{string}: Didn't parse correctly")
        if "VOLT" in string:
            if "@1" in string:
                return self.deviceDict_["ch1v"]
            if "@2" in string:
                return self.deviceDict_["ch2v"]
            raise ValueError(f"{string}: Didn't parse correctly")
        if "SYST:ERR" in string:
            return '+0,"No error"'
        raise ValueError(f"{string}: Didn't parse correctly")