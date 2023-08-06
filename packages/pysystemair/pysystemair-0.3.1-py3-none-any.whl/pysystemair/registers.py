from box import Box

from .models import (
     InputRegister
    ,HoldingRegister
)

registers = Box({
    #Input registers
     "sa_target_temperature_"      : InputRegister(addr=2053) # REG_TC_SP_SATC: Temperature setpoint for the supply air temperature
    ,"remaining_filter_time_"      : InputRegister(addr=7004) # REG_FILTER_REMAINING_TIME_L: Remaining filter time in seconds, lower 16 bits
    ,"heat_exchanger_"              : InputRegister(addr=14102) # REG_OUTPUT_Y2_ANALOG: Heat Exchanger AO state.
    ,"heat_exchanger_active_"        : InputRegister(addr=14103) # REG_OUTPUT_Y2_DIGITAL: Heat Exchanger DO state.0: Output not active1: Output active
    # heater_a0                 : InputRegister(addr=14100)# REG_OUTPUT_Y1_ANALOG: Heater AO state.
    ,"heater_active_"                 : InputRegister(addr=14101) # REG_OUTPUT_Y1_DIGITAL: Heater DO state:0: Output not active1: Output active
    ,"filter_alarm_"               : InputRegister(addr=7006) # REG_FILTER_ALARM_WAS_DETECTED: Indicates if the filter warning alarm was generated.
    ,"usermode_"                   : InputRegister(addr=1160) # REG_USERMODE_MODE: Active User mode.0: Auto1: Manual2: Crowded3: Refresh4: Fireplace5: Away6: Holiday7: Cooker Hood8: Vacuum Cleaner9: CDI110: CDI211: CDI312: PressureGuard
    # speed_saf_desired_off     : InputRegister(addr=1351) # REG_SPEED_SAF_DESIRED_OFF: Indicates that the SAF shall be turned off once the electrical reheater is cooled down
    ,"saf_speed_"                  : InputRegister(addr=14370)  # REG_OUTPUT_FAN_SPEED1: Supply air fan control signal in %
    ,"eaf_speed_"                  : InputRegister(addr=14371)  # REG_OUTPUT_FAN_SPEED2: Extract air fan control signal in %
    # speed_saf_desired_off     : InputRegister(addr=1351) 
    # speed_saf_desired_off     : InputRegister(addr=1351) 
    # speed_saf_desired_off     : InputRegister(addr=1351) 
    
    #HoldingRegister
    ,"target_temperature"          : HoldingRegister(addr=2000)   # REG_TC_SP: Temperature setpoint for the supply air temperature
    ,"sa_temperature_sensor"       : HoldingRegister(addr=12102)   # REG_SENSOR_SAT: Supply Air Temperature sensor (standard)
    ,"oa_temperature_sensor"       : HoldingRegister(addr=12100)   # REG_SENSOR_OAT: Outdoor Air Temperature sensor (standard)
    ,"saf_usermode_fs"             : HoldingRegister(addr=1130)    # REG_USERMODE_MANUAL_AIRFLOW_LEVEL_SAF:  Fan speed level for mode Manual, supply fan.(1): value Off only allowed if contents of register 1352 is 1: Off 2: Low 3: Normal 4:High
    ,"eaf_usermode_fs"             : HoldingRegister(addr=1131)   # REG_USERMODE_MANUAL_AIRFLOW_LEVEL_EAF Fan speed level for mode Manual, extract fan. 2: Low 3: Normal 4: High
    ,"usermode"                    : HoldingRegister(addr=1161)   # REG_USERMODE_HMI_CHANGE_REQUEST: New desired user mode as requested bMI0: None1: AUTO2: Manual 3: Crowded4:Refresh5: Fireplace6: Away7: Holiday
    ,"pdm_humidity_sensor"         : HoldingRegister(addr=12135)   # REG_SENSOR_RHS_PDM: PDM RHS sensor value (standard)
    # REG_SENSOR_PDM_EAT_VALUE  : = HoldingRegister(addr=12543)  # REG_SENSOR_PDM_EAT_VALUE: PDM EAT sensor value (standard)
    # REG_TC_CASCADE_SP_MIN     : = HoldingRegister(addr=2020)  # REG_TC_CASCADE_SP_MIN: Minimum temperature set point for the SATC
    # REG_TC_CASCADE_SP_MAX     : = HoldingRegister(addr=2021)  # REG_TC_CASCADE_SP_MAX: Maximum temperature set point for the SATC
    ,"target_humidity"             : HoldingRegister(addr=2202) #REG_ROTOR_RH_TRANSFER_CTRL_SETPOINT: Set point setting for RH transfer contro
    ,"co2_sensor"                  : HoldingRegister(addr=12115) # REG_SENSOR_CO2S: CO2 value (accessory)
    ,"cooling_recovery_limit"      : HoldingRegister(addr=2314) # REG_COOLER_RECOVERY_LIMIT_T:Temperature at which cooling recovery is allowed
    ,"cooling_recovery_enabled"    : HoldingRegister(addr=2133)  #REG_HEAT_EXCHANGER_COOLING_RECOVERY_ON_OFF: Enabling of cooling recovery
    ,"free_cooling_enabled"        : HoldingRegister(addr=12135)  #REG_FREE_COOLING_ON_OFF: Indicates if free cooling is enabled
    ,"free_cooling_start_time_h"   : HoldingRegister(addr=4105) # REG_FREE_COOLING_START_TIME_H: Start time of free cooling night-period, hour.Valid range is from 0 to 8 and from 21 to 23.
    ,"free_cooling_start_time_m"   : HoldingRegister(addr=4106) # REG_FREE_COOLING_START_TIME_M: 0 59 Start time of free cooling night-period,Minute
    ,"free_cooling_end_time_h"     : HoldingRegister(addr=4107) # REG_FREE_COOLING_END_TIME_H: End time of free cooling night-period, hour.Valid range is from 0 to 8 and from 21 to 23.
    ,"free_cooling_end_time_m"     : HoldingRegister(addr=4108) # REG_FREE_COOLING_END_TIME_M: 0 59 End time of free cooling night-period, Minute
    ,"free_cooling_active"         : HoldingRegister(addr=4110) # REG_FREE_COOLING_ACTIVE: 0 1 Indicates if free cooling is being performed
    # humidity                    = HoldingRegister(addr=12135) 
    # humidity                    = HoldingRegister(addr=12135) 
    # humidity                    = HoldingRegister(addr=12135) 
    # humidity                    = HoldingRegister(addr=12135) 
    # humidity                    = HoldingRegister(addr=12135)         
    # humidity                    = HoldingRegister(addr=12135) 

})