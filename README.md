# pytestmock
Minimum working example of issue

py -m pip install -r requirements.txt

uut has the mocked method for pyvisa resourceManager_.open_resource going into the yield
has it in the device_mock object during the test
it disappears when control returns to the pytest fixture and reverts to the pyvisa library call