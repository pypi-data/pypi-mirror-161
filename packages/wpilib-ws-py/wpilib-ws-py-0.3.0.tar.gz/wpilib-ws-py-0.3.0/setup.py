# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wpilib_ws']

package_data = \
{'': ['*']}

install_requires = \
['websockets>=10.0,<11.0']

setup_kwargs = {
    'name': 'wpilib-ws-py',
    'version': '0.3.0',
    'description': 'An implementation of the WPILib WebSocket protocol for Python',
    'long_description': '# wpilib-ws-py\n\nThis library is an implementation of the WPILib simulation WebSocket, used for controlling non-frc hardware or simulation software using WPILib. The specification of this protocol is found [here](https://github.com/wpilibsuite/allwpilib/blob/main/simulation/halsim_ws_core/doc/hardware_ws_api.md).\n\nMy own dive into the source code for the websocket, which has some undocumented information: https://github.com/AM2i9/wpilib-ws-py/payloads.md\n\n[Example Sever Usage](https://github.com/AM2i9/wpilib-ws-py/tests/examples/demo_server.py):\n\n```py\nfrom wpilib_ws import WPILibWsServer\n\nserver = WPILibWsServer()\n\n# The on_message decorator will let you create handlers for message events.\n# Optionally a device type can be entered to only handle messages for that\n# specific device type. A list of device types and other hardware messages can\n# be found here:\n# https://github.com/wpilibsuite/allwpilib/blob/main/simulation/halsim_ws_core/doc/hardware_ws_api.md#hardware-messages\n\n\n@server.on_message("PWM")\nasync def pwm_handler(message):\n    payload = message.data\n    print(f"Recieved PWM event: {payload}")\n    # ...\n\n\n@server.on_message("CANMotor")\nasync def can_motor_handler(message):\n    payload = message.data\n    print(f"Recieved CANMotor event: {payload}")\n    # ...\n\n\n# Optionally, a device name can be entered to `on_message()`:\n\n\n@server.on_message("SimDevice", "SPARK MAX")\nasync def spark_max_handler(message):\n\n    # SimDevices are arbitrary devices sent over the websocket, which can be\n    # used by vendor libraries to be able to use their controllers in robot\n    # simulation. For example, SPARK MAX and other REV controllers will not\n    # show as CAN devices, but as SimDevices.\n\n    payload = message.data\n    print(f"Recieved update for SPARK MAX controller: {payload}")\n\n\n@server.on_message("CANMotor", "Victor SPX")\nasync def victor_handler(message):\n    payload = message.data\n    print(f"Recieved update for Victor SPX controller: {payload}")\n\n\n# The while_connected decorator is a loop that runs alongside the server, and\n# can be used for periodic tasks, such as sending battery voltage, like below.\n@server.while_connected()\nasync def while_connected():\n    await server.send_payload(\n        {"type": "RoboRIO", "device": "", "data": {">vin_voltage": 12.0}}\n    )\n\n\nserver.run()\n```',
    'author': 'Patrick Brennan (AM2i9)',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AM2i9/wpilib-ws-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
