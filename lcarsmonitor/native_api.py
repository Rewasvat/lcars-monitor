import os
import clr

# from C# .NET
from System.Reflection import Assembly  # type: ignore

dll_name = "LibreHardwareMonitorLib.dll"
dll_path = os.path.join(os.path.dirname(__file__), dll_name)
Assembly.UnsafeLoadFrom(dll_path)

from LibreHardwareMonitor.Hardware import Computer, ISensor, SensorType  # type: ignore
from System import Enum as CEnum  # type: ignore

all_sensor_types = [str(t) for t in CEnum.GetValues(SensorType)]
