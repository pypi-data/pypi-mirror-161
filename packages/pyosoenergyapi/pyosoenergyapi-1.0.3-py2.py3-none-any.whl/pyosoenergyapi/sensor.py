"""OSO Energy Sensor Module."""

from .helper.const import sensor_commands


class OSOEnergySensor:
    # pylint: disable=no-member
    """OSO Energy Sensor Code."""

    sensorType = "Sensor"
    hotwaterType = "Hotwater"
    hotwaterConnection = "HeaterConnection"

    def get_state(self, device: dict):
        """Get sensor state.

        Args:
            device (dict): Device to get state off.

        Returns:
            srt: State of device
        """
        state = None
        final = None

        try:
            data = self.session.data.sensors[device["device_id"]]
            if data["type"] == "":
                state = data[""]
                final = state
            elif data["type"] == "":
                final = data[""]
        except KeyError as exception:
            self.session.log.error(exception)

        return final


class Sensor(OSOEnergySensor):
    """Home Assistant sensor code.

    Args:
        OSOEnergySensor (object): OSO Energy sensor code.
    """

    def __init__(self, session: object = None):
        """Initialise sensor.

        Args:
            session (object, optional): session to interact with OSO Energy. Defaults no None.
        """
        self.session = session

    def get_sensor(self, device: dict):
        # pylint: disable=eval-used
        """Get updated sensor data.

        Args:
            device (dict): Device to update.

        Returns:
            dict: Updated device.
        """
        device.update({"online": self.session.attr.online_offline(device["device_id"])})

        if device["online"]:
            self.session.helper.device_recovered(device["device_id"])
            dev_data = {}
            dev_data = {
                "haName": device["haName"],
                "haType": device["haType"],
                "osoEnergyType": device["osoEnergyType"],
                "device_id": device["device_id"],
                "device_type": device["device_type"],
                "device_name": device["device_name"],
                "available": self.session.attr.online_offline(device["device_id"])
            }

            if dev_data["osoEnergyType"] in sensor_commands:
                code = sensor_commands.get(dev_data["osoEnergyType"])
                dev_data.update(
                    {
                        "status": {"state": eval(code)}
                    }
                )

            self.session.sensors.update({device["device_id"]: dev_data})
            return self.session.sensors[device["device_id"]]

        self.session.log.error_check(
            device["device_id"], device["online"]
        )
        return device
