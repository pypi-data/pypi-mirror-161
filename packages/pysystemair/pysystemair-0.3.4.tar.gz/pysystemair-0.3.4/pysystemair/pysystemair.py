from typing import Awaitable, Callable
from functools import partial
import logging
_LOGGER = logging.getLogger(__name__)

from .const import *
from .models import Callbacks, Register
from .registers import registers



class PySystemAir():

    _async_callbacks: Callbacks

    def __init__(self, async_callbacks:Callbacks=None):
        _LOGGER.info(f"New SYSTEMAIR MODULE")
        if async_callbacks is not None:
            self._async_callbacks=async_callbacks
        else:
            from pymodbus.client.asynchronous.serial import AsyncModbusSerialClient as Client
            event_loop, client = Client(port='/dev/ttyUSB0',
                      stopbits=1,
                      bytesize=8,
                      parity='E',
                      baudrate=56000,
                      timeout=2)
            client.connect()
            # client.read_holding_registers()
            # holding_reg_callback=partial(client.read_holding_registers, 
            self._async_callbacks = Callbacks(holding_reg=client.read_holding_registers, input_reg=client.read_input_registers, write_reg=client.write_register)
            # callbacks_accepted=True
            # if iscoroutinefunction(async_callbacks['holding_reg']):
            #     self._async_callbacks.holding_reg=async_callbacks['holding_reg']
            # else
            # self._async_callbacks.input_reg=async_callback_input_reg
            # self._async_callbacks.write_reg=async_callback_write_reg

        # registers = RegMap


    async def async_update_all(self):
        """
        Updates all of the input and holding regs dict values.
        """
       
        for key, register in registers.items():
            # _LOGGER.warning(f"Updating register for {key} {register}")
            # _LOGGER.warning(f"register.addr == {register.addr}")
            # _LOGGER.warning(f"register.reg_type == {register.reg_type}")
            try:
                await self.async_update_from_register(key, register)
                # result=None
                # if register.reg_type == REG_TYPE.INPUT:
                #     result = await self._async_callbacks.input_reg(address=register.addr)
                # elif register.reg_type == REG_TYPE.HOLDING:
                #     result = await self._async_callbacks.holding_reg(address=register.addr)
                # else:
                #     _LOGGER.warning(f"register.reg_type not matched")
                # # _LOGGER.warning(f"result= {result}")
                # if result is None:
                #     _LOGGER.warning(f"Error reading {variable} value from SystemAir modbus adapter")
                # else:
                #     register.value = result.registers[0]
            except AttributeError:
                 _LOGGER.warning(f"Modbus read failed for {key}")

    async def async_update_from_register(self, key, register:Register):
        """
        Updates all of the input and holding regs dict values.
        """
        try:
            result=None
            _LOGGER.warning(f"register.addr == {register.addr}")
            _LOGGER.warning(f"register.reg_type == {register.reg_type}")
            if register.reg_type == REG_TYPE.INPUT:
                _LOGGER.warning(f"calling {self._async_callbacks.input_reg}")
                result = await self._async_callbacks.input_reg(address=register.addr)
            elif register.reg_type == REG_TYPE.HOLDING:
                _LOGGER.warning(f"calling {self._async_callbacks.holding_reg}")
                result = await self._async_callbacks.holding_reg(address=register.addr)

            if result is None:
                 _LOGGER.warning(f"Error reading {key} value from SystemAir modbus adapter")
            else:
                _LOGGER.warning(f"{key} value is {result.registers[0]}")
                register.value = result.registers[0]
        except AttributeError as e:
            raise e


    async def async_write_to_register(self, register:Register, value):
        """
        Updates all of the input and holding regs dict values.
        """
        try:
            if await self._async_callbacks.write_reg(address=register.addr, value=value):
                    register.value = value
            else:
                _LOGGER.error(f"Unable to write {value} to register {register.addr}") 
        except AttributeError as e:
            raise e

    # @property
    # def user_modes(self):
    #     """Return the fan setting."""
    #     return list( USER_MODES.values())




    @property
    def fan_mode(self):
        """Return the fan setting."""
        if registers.saf_usermode_fs.value is None:
            return 3
        return registers.saf_usermode_fs.value



    @property
    def filter_hours(self):
        if registers.remaining_filter_time_.value is None:
            return 0
        return registers.remaining_filter_time_.value 

    @property
    def filter_alarm(self):
        if registers.filter_alarm_.value is None:
            return 0
        return registers.filter_alarm_.value

    @property
    def heat_exchanger_active(self):
        if registers.heat_exchanger_active_.value is None:
            return 0
        return registers.heat_exchanger_active_.value
    
    @property
    def heat_exchanger(self):
        if registers.heat_exchanger_.value is None:
            return 0
        return registers.heat_exchanger_.value

 
    # @property
    # def heating(self):
    #     if registers.oa_temperature_sensor.value is None:
    #         return 0
    #     return registers.oa_temperature_sensor.value / 10.0


    @property
    def heater_enabled(self):
        if registers.heater_active_.value is None:
            return 0
        return registers.heater_active_.value

    # @property
    # def cooling_enabled(self):  
    #     if registers.oa_temperature_sensor.value is None:
    #         return 0
    #     return registers.oa_temperature_sensor.value / 10.0


    @property
    def free_cooling_enabled(self): 
        if registers.free_cooling_enabled.value is None:
            return 0
        return registers.free_cooling_enabled.value


    @property
    def free_cooling_active(self):
        if registers.free_cooling_active.value is None:
            return 0
        return registers.free_cooling_active.value


    @property
    def free_cooling_start_time(self):
        if registers.free_cooling_start_time_h.value is None or registers.free_cooling_start_time_m.value is None:
            return 0
        return f"{registers.free_cooling_start_time_h.value}:{registers.free_cooling_start_time_m.value}"

    @property
    def free_cooling_end_time(self): 
        if registers.free_cooling_end_time_h.value is None or registers.free_cooling_end_time_m.value is None:
            return 0
        return f"{registers.free_cooling_end_time_h.value}:{registers.free_cooling_end_time_m.value}"

    @property
    def outdoor_air_temp(self):
        if registers.oa_temperature_sensor.value is None:
            return 0
        return registers.oa_temperature_sensor.value / 10.0


    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if registers.target_temperature.value is None:
            return 0
        return registers.target_temperature.value / 10.0

    @property
    def current_temperature(self):
        """Return the current temperature."""
        if registers.sa_temperature_sensor.value is None:
            return 0
        return registers.sa_temperature_sensor.value / 10

    @property
    def current_humidity(self):
        """Return the temperature we try to reach."""
        if registers.pdm_humidity_sensor.value is None:
            return 0
        return registers.pdm_humidity_sensor.value

    @property
    def target_humidity(self):
        """Return the temperature we try to reach."""
        if registers.target_humidity.value is None:
            return 0
        return registers.target_humidity.value


    async def async_set_temperature(self, value):
        """Set new target temperature."""
        await self.async_write_to_register(registers.target_temperature, value)


    async def async_set_fan_mode(self, value):
        """Set new fan mode."""
        value = FAN_MODES(value)
        await self.async_write_to_register(registers.saf_usermode_fs, value)
        await self.async_write_to_register(registers.eaf_usermode_fs, value)


    async def async_set_humidity(self, value):
        """Set new target temperature."""
        target_humidity=int(round(value))
        

    async def async_cotwo_meas(self, value):
        """Set new target temperature."""
        await self.async_write_to_register(registers.co2_sensor, value)