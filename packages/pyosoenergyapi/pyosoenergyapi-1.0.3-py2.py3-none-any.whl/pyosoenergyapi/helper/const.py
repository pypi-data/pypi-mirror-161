"""OSO Energy constants."""
# pylint: disable=line-too-long
# HTTP return codes.
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_MOVED_PERMANENTLY = 301
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503

OSOTOHA = {
    "Hotwater": {
        "HeaterState": {"on": "on", "off": "off"},
        "DeviceConstants": {"minTemp": 10, "maxTemp": 80},
        "HeaterConnection": {None: False, "Connected": True},
        "HeaterMode": {
            None: "off",
            "auto": "auto",
            "manual": "manual",
            "off": "off",
            "Legionella": "legionella",
            "PowerSave": "powerSave",
            "ExtraEnergy": "extraEnergy",
            "Voltage": "voltage"
        },
        "HeaterOptimizationMode": {None: "off"},
        "HeaterSubOptimizationMode": {None: None},
        "HeaterPowerSaveMode": {None: "off", False: "off", True: "on"},
        "HeaterExtraEnergyMode": {None: "off", False: "off", True: "on"},
    }
}

sensor_commands = {
    "POWER_SAVE": "self.session.attr.get_power_save(device[\"device_id\"])",
    "EXTRA_ENERGY": "self.session.attr.get_extra_energy(device[\"device_id\"])",
    "POWER_LOAD": "self.session.attr.get_actual_load_kwh(device[\"device_id\"])",
    "VOLUME": "self.session.attr.get_volume(device[\"device_id\"])",
    "TAPPING_CAPACITY_KWH": "self.session.attr.get_tapping_capacity_kwh(device[\"device_id\"])",
    "CAPACITY_MIXED_WATER_40": "self.session.attr.get_capacity_mixed_water_40(device[\"device_id\"])",
    "HEATER_STATE": "self.session.attr.get_heater_state(device[\"device_id\"])",
    "HEATER_MODE": "self.session.attr.get_heater_mode(device[\"device_id\"])",
    "OPTIMIZATION_MODE": "self.session.attr.get_optimization_mode(device[\"device_id\"])",
    "V40_MIN": "self.session.attr.get_v40_min(device[\"device_id\"])",
    "PROFILE": "self.session.attr.get_profile(device[\"device_id\"])"
}
