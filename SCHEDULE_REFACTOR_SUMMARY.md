# YoLink Schedule System Refactor

## Overview

The `udiYoSchedule.py` file has been refactored to use a class hierarchy approach where different device types use appropriate schedule node classes. This provides better code organization, reusability, and maintainability.

## Architecture

### Class Hierarchy

```
BaseScheduleNode (abstract base)
├── OnOffScheduleNode (Switch, Outlet, Dimmer, Manipulator)
│   ├── SprinklerScheduleNode (Sprinkler, SprinklerV2)
│   └── WaterMeterScheduleNode (WaterMeterController, WaterMeterMultiController)
├── KeyScheduleNode (InfraredRemoter)
└── MultiOutletScheduleNode (MultiOutlet)
```

### Classes

#### BaseScheduleNode
Common functionality for all schedule nodes:
- Schedule data fetching and caching
- Time string parsing (HH:MM and HH:MM:SS formats)
- Driver updates for schedule display
- Schedule activation/deactivation
- UI command handling (UPDATE, LOOKUPSCH, CTRLSCH)

**Key Methods:**
- `_parse_time_string()` - Parse YoLink time format
- `_update_time_drivers()` - Update UI drivers with time information
- `_update_schedule_display()` - Update all UI drivers with schedule data
- `activate_schedule()` - Parse activation commands
- `updateData()` - Refresh schedule display from device

#### OnOffScheduleNode
For devices that trigger on/off state changes at scheduled times.

**Supported Devices:**
- Switch
- Outlet
- Dimmer
- Manipulator

**Schedule Parameters:**
- `index` - Schedule number (0-9)
- `isValid` - Schedule enabled/disabled
- `on` - Time to turn on (HH:MM or HH:MM:SS)
- `off` - Time to turn off (HH:MM or HH:MM:SS)
- `week` - Weekday bitmask (0-127)

**Special Handling:**
- Time value "25:00" means "not set"
- Supports optional seconds field based on device capability

#### SprinklerScheduleNode
Inherits from `OnOffScheduleNode` for Sprinkler and SprinklerV2 watering schedules.

**Supported Devices:**
- Sprinkler
- SprinklerV2

**Schedule Parameters:**
- `index` - Schedule index (0-9)
- `valid` - Schedule enabled/disabled
- `time` - Start time (HH:MM)
- `days` - Repeat type and weekly bitmask (`{'type': 'weekly', 'value': mask}`)
- `startDate` / `endDate` - Seasonal date constraints (defaults to `1-1` and `12-31`)
- `waterDelay` - Duration / rain delay settings (`{'type': 'duration', 'value': 0}`)

**Special Handling:**
- Maps SprinklerV2 structure (`time`, `days`, `valid`) to generic schedule display drivers
- Preserves repeat type and water delay settings across UI edits
- Node ID: `YOSPRINKLERSCHEDULE` or `YOSPRINKLERSCHEDULESEC` when seconds are supported

#### WaterMeterScheduleNode
Inherits from `OnOffScheduleNode` for WaterMeterController and WaterMeterMultiController valve and leak schedules.

**Supported Devices:**
- WaterMeterController
- WaterMeterMultiController

**Schedule Parameters:**
- `index` - Schedule number (0-9)
- `isValid` - Schedule enabled/disabled
- `on` / `off` - Valve or leak schedule window times (HH:MM or HH:MM:SS)
- `week` - Weekday bitmask
- `leakLimit` - Leak volume threshold limit (for leak schedules)

**Special Handling:**
- Configurable via `schedule_type`: `'valve'` (valve control schedules) or `'leak'` (leak detection schedules)
- Uses device-specific API methods (`getValveSchedules`/`setValveSchedules` or `getLeakSchedules`/`setLeakSchedules`)
- GV12 driver displays the configured leak limit value
- Node ID: `YOWMSCHEDULE`

#### KeyScheduleNode
For infrared remote devices that transmit IR codes on schedule.

**Supported Devices:**
- InfraredRemoter

**Schedule Parameters:**
- `key` - Infrared code index to transmit
- `on` - Time to transmit code
- `off` - Secondary time (may not be used)
- `week` - Weekday bitmask

**Special Handling:**
- GV12 driver displays selected IR key code
- Extended schedule ID when seconds are supported

#### MultiOutletScheduleNode
For multi-outlet devices with per-channel scheduling.

**Supported Devices:**
- MultiOutlet

**Schedule Parameters:**
- `ch` - Channel/outlet number (0-based)
- `on` - Time to turn on
- `off` - Time to turn off
- `week` - Weekday bitmask

**Special Handling:**
- GV12 driver displays selected channel number
- Each outlet can have independent schedules

### Factory Function

The `udiYoSchedule()` function acts as a factory that instantiates the correct schedule node class based on device type:

```python
def udiYoSchedule(polyglot, primary, address, name, yoAccess, deviceInfo, schedule_type='valve'):
    """Factory function maintaining backward compatibility"""
    dev_type = deviceInfo.get('type', '')
    
    if dev_type == 'InfraredRemoter':
        return KeyScheduleNode(...)
    elif dev_type in ['MultiOutlet']:
        return MultiOutletScheduleNode(...)
    elif dev_type in ['SprinklerV2', 'Sprinkler']:
        return SprinklerScheduleNode(...)
    elif dev_type in ['WaterMeterController', 'WaterMeterMultiController']:
        return WaterMeterScheduleNode(..., schedule_type=schedule_type)
    else:  # Default to OnOff for Switch, Outlet, Dimmer, Manipulator, etc.
        return OnOffScheduleNode(...)
```

**Benefits:**
- Existing code using `udiYoSchedule()` continues to work unchanged
- Automatic routing to correct schedule class
- Easy to extend to new device types

## Usage in Device Nodes

Existing device nodes (udiYoOutletV4.py, udiYoSwitchV4.py, etc.) continue to work without modification:

```python
from udiYoSchedule import udiYoSchedule

# In start() method:
sch_address = self.address[4:14] + '_SCH'
sch_address = self.poly.getValidAddress(sch_address)
self.schedule = udiYoSchedule(self.poly, self.address, sch_address, 
                              'Schedules', self.yoAccess, self.devInfo)
```

The factory function automatically creates the correct schedule node type.

## Driver Layout (Common to All Types)

| Driver | Name | Purpose | Note |
|--------|------|---------|------|
| GV12 | Channel/Key | Channel (MultiOutlet) or Key (IR Remote) | Optional |
| GV13 | Schedule Index | Which schedule (0-9) | All types |
| GV14 | Active | Is schedule enabled? | All types |
| GV15 | On Hour | Start hour (0-25) | All types |
| GV16 | On Minute | Start minute (0-59) | All types |
| GV21 | On Second | Start second (0-59) | With seconds support |
| GV17 | Off Hour | Stop hour (0-25) | All types |
| GV18 | Off Minute | Stop minute (0-59) | All types |
| GV22 | Off Second | Stop second (0-59) | With seconds support |
| GV19 | Weekday Mask | Days to run (binary) | All types |

## Extending to New Device Types

To add schedule support for a new device type:

1. Create a new subclass of `BaseScheduleNode`:
```python
class MyDeviceScheduleNode(BaseScheduleNode):
    id = 'myoschedule'
    drivers = [...]  # Your driver list
    
    def prep_schedule(self, query):
        # Parse device-specific parameters
        # Call parent's common parsing
        pass
```

2. Update the factory function:
```python
def udiYoSchedule(...):
    if dev_type == 'InfraredRemoter':
        return KeyScheduleNode(...)
    elif dev_type == 'MyNewDevice':
        return MyDeviceScheduleNode(...)
    # ...
```

## Benefits of Refactored Design

✅ **Code Reuse** - Common schedule logic in BaseScheduleNode  
✅ **Maintainability** - Device-specific logic isolated in subclasses  
✅ **Extensibility** - Easy to add new schedule types  
✅ **Clarity** - Clear separation of concerns  
✅ **Backward Compatible** - Factory function preserves existing API  
✅ **Testability** - Each class can be tested independently  

## Migration Notes

### No Changes Required
- Device node code (udiYoOutletV4.py, udiYoSwitchV4.py, etc.)
- MQTT handling (yolink_mqtt_classV4.py)
- Schedule display helpers in udiYolinkLib.py

### What Changed
- Internal organization of udiYoSchedule.py
- Better documentation and type clarity
- More flexible architecture for future extensions
