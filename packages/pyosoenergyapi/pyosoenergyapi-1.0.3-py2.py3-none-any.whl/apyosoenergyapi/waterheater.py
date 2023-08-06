"""OSO Energy Water Heater Module."""

from array import array
from numbers import Number
from aiohttp.web_exceptions import HTTPError
from .helper.const import OSOTOHA


class OSOWaterHeater:
    # pylint: disable=no-member
    """Water Heater Code.

    Returns:
        object: Water Heater Object
    """

    hotwaterType = "Hotwater"

    async def get_heater_state(self, device: dict):
        """Get water heater current mode.

        Args:
            device (dict): Device to get the mode for.

        Returns:
            str: Return mode.
        """
        state = None
        final = None

        try:
            device = self.session.data.devices[device["device_id"]]
            state = device["control"]["heater"]
            final = OSOTOHA[self.hotwaterType]["HeaterState"].get(state, state)
        except KeyError as exception:
            await self.session.log.error(exception)

        return final

    async def turn_on(self, device: dict, full_utilization: bool):
        """Turn device on.

        Args:
            device (dict): Device to turn on.
            full_utilization (bool): Fully utilize device.

        Returns:
            boolean: return True/False if turn on was successful.
        """
        final = False

        try:
            resp = await self.session.api.turn_on(device["device_id"], full_utilization)
            if resp["original"] == 200:
                final = True
                await self.session.get_devices()

        except HTTPError as exception:
            await self.session.log.error(exception)

        return final

    async def turn_off(self, device: dict, full_utilization: bool):
        """Turn device off.

        Args:
            device (dict): Device to turn off.
            full_utilization (bool): Fully utilize device.

        Returns:
            boolean: return True/False if turn off was successful.
        """
        final = False

        try:
            resp = await self.session.api.turn_off(device["device_id"], full_utilization)
            if resp["original"] == 200:
                final = True
                await self.session.get_devices()

        except HTTPError as exception:
            await self.session.log.error(exception)

        return final

    async def set_v40_min(self, device: dict, v40min: float):
        """Set V40 Min levels for device.

        Args:
            device (dict): Device to turn off.
            v40Min (float): quantity of water at 40°C.

        Returns:
            boolean: return True/False if setting the V40Min was successful.
        """
        final = False

        try:
            resp = await self.session.api.set_v40_min(device["device_id"], v40min)
            if resp["original"] == 200:
                final = True
                await self.session.get_devices()

        except HTTPError as exception:
            await self.session.log.error(exception)

        return final

    async def set_optimization_mode(self, device: dict, option: Number, sub_option: Number):
        """Set heater optimization mode.

        Args:
            device (dict): Device to turn off.
            option (Number): heater optimization option.
            sub_option (Number): heater optimization sub option.

        Returns:
            boolean: return True/False if setting the optimization mode was successful.
        """
        final = False

        try:
            resp = await self.session.api.set_optimization_mode(
                device["device_id"],
                optimizationOptions=option,
                optimizationSubOptions=sub_option
            )
            if resp["original"] == 200:
                final = True
                await self.session.get_devices()

        except HTTPError as exception:
            await self.session.log.error(exception)

        return final

    async def set_profile(self, device: dict, profile: array):
        """Set heater profile.

        Args:
            device (dict): Device to set profile to.
            profile (array): array of temperatures for 24 hours (UTC).

        Returns:
            boolean: return True/False if setting the profile was successful.
        """
        final = False

        try:
            resp = await self.session.api.set_profile(device["device_id"], hours=profile)
            if resp["original"] == 200:
                final = True
                await self.session.get_devices()

        except HTTPError as exception:
            await self.session.log.error(exception)

        return final


class WaterHeater(OSOWaterHeater):
    """Water heater class.

    Args:
        OSOWaterHeater (object): OSOWaterHeater class.
    """

    def __init__(self, session: object = None):
        """Initialise water heater.

        Args:
            session (object, optional): Session to interact with account. Defaults to None.
        """
        self.session = session

    async def get_water_heater(self, device: dict):
        """Update water heater device.

        Args:
            device (dict): device to update.

        Returns:
            dict: Updated device.
        """
        device.update({"online": await self.session.attr.online_offline(device["device_id"])})

        if(device["online"]):
            dev_data = {}
            self.session.helper.device_recovered(device["device_id"])
            dev_data = {
                "haName": device["haName"],
                "haType": device["haType"],
                "device_id": device["device_id"],
                "device_type": device["device_type"],
                "device_name": device["device_name"],
                "status": {"current_operation": await self.get_heater_state(device)},
                "attributes": await self.session.attr.state_attributes(
                    device["device_id"]
                ),
            }

            self.session.devices.update({device["device_id"]: dev_data})
            return self.session.devices[device["device_id"]]

        await self.session.log.error_check(
            device["device_id"], device["online"]
        )
        return device
