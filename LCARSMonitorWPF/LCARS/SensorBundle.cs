using LibreHardwareMonitor.Hardware;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace LCARSMonitor.LCARS
{
    public class SensorBundle : IVisitor
    {
        // PROPERTIES
        public ILCARSSensorHandler Parent { get; protected set; }
        public Dictionary<string, ISensor> Sensors { get; protected set; }
        private Dictionary<ISensor, bool> updatedSensors;

        // CONSTRUCTOR
        public SensorBundle(ILCARSSensorHandler parent)
        {
            Parent = parent;
            Sensors = new Dictionary<string, ISensor>();
            updatedSensors = new Dictionary<ISensor, bool>();
        }

        // IVisitor IMPLEMENTATION
        public void VisitComputer(IComputer computer) { }
        public void VisitParameter(IParameter parameter) { }

        public void VisitHardware(IHardware hardware)
        {
            if (Sensors.Count <= 0)
                return;

            if (!LCARSSystem.Global.IsHardwareUpdated(hardware))
            {
                hardware.Update();
                LCARSSystem.Global.MarkHardwareUpdated(hardware);
                foreach (IHardware subHardware in hardware.SubHardware)
                {
                    subHardware.Accept(this);
                }
            }
        }

        public void VisitSensor(ISensor sensor)
        {
            updatedSensors[sensor] = true;
        }

        // METHODS

        public void SetSensors(string[] sensorIDs)
        {
            Sensors.Clear();
            updatedSensors.Clear();

            foreach (ISensor sensor in LCARSSystem.Global.GetSensorsByIDs(sensorIDs))
            {
                Sensors[sensor.Identifier.ToString()] = sensor;
                updatedSensors[sensor] = false;

                Parent.OnSensorUpdate(sensor);
            }
            System.Diagnostics.Debug.WriteLine($"GET SENSORS: found {Sensors.Count} sensors from {sensorIDs}");
        }

        public void AsyncUpdate()
        {
            foreach (ISensor sensor in Sensors.Values)
            {
                sensor.Hardware.Accept(this);
                sensor.Accept(this);
            }
        }

        public void Update()
        {
            foreach (var sensor in Sensors.Values)
            {
                if (updatedSensors[sensor])
                {
                    Parent.OnSensorUpdate(sensor);
                }
                updatedSensors[sensor] = false;
            }
        }
    }

    public interface ILCARSSensorHandler
    {
        public SensorBundle SensorBundle { get; }
        public void OnSensorUpdate(ISensor sensor);
    }

    public static class ISensorExtensions
    {
        public static string GetSensorUnit(this ISensor sensor)
        {
            string unit;
            switch (sensor.SensorType)
            {
                case SensorType.Voltage:
                    unit = "V";
                    break;
                case SensorType.Current:
                    unit = "A";
                    break;
                case SensorType.Clock:
                    unit = "MHz";
                    break;
                case SensorType.Load:
                case SensorType.Level:
                case SensorType.Control:
                    unit = "%";
                    break;
                case SensorType.Temperature:
                    unit = "°C";
                    break;
                case SensorType.Fan:
                    unit = "RPM";
                    break;
                case SensorType.Flow:
                    unit = "L/h";
                    break;
                case SensorType.Power:
                    unit = "W";
                    break;
                case SensorType.Data:
                    unit = "GB";
                    break;
                case SensorType.SmallData:
                    unit = "MB";
                    break;
                case SensorType.Factor:
                    unit = "<no-unit>";
                    break;
                case SensorType.Frequency:
                    unit = "Hz";
                    break;
                case SensorType.Throughput:
                    unit = "B/s";
                    break;
                case SensorType.TimeSpan:
                    unit = "s";
                    break;
                case SensorType.Energy:
                    unit = "mWh";
                    break;
                // case SensorType.Noise:
                //     unit = "dBA";
                //     break;
                default:
                    unit = "<unknown-unit>";
                    break;
            }
            return unit;
        }

        public static string GetSensorValueFormat(this ISensor sensor)
        {
            string format;
            switch (sensor.SensorType)
            {
                case SensorType.Voltage:
                case SensorType.Current:
                case SensorType.Factor:
                    format = "{0:F3}";
                    break;
                case SensorType.Clock:
                case SensorType.Load:
                case SensorType.Temperature:
                case SensorType.Flow:
                case SensorType.Control:
                case SensorType.Level:
                case SensorType.Power:
                case SensorType.Data:
                case SensorType.SmallData:
                case SensorType.Frequency:
                case SensorType.Throughput:
                    format = "{0:F1}";
                    break;
                case SensorType.Fan:
                case SensorType.Energy:
                    // case SensorType.Noise:
                    format = "{0:F0}";
                    break;
                case SensorType.TimeSpan:
                    format = "{0:g}";
                    break;
                default:
                    format = "{0}";
                    break;
            }
            return format;
        }

        private static object? GetSensorAttribute(this ISensor sensor, string key)
        {
            switch (key.ToLower())
            {
                case "id":
                case "identifier":
                    return sensor.Identifier;
                case "name":
                    return sensor.Name;
                case "min":
                case "minimum":
                    return sensor.Min;
                case "max":
                case "maximum":
                    return sensor.Max;
                case "value":
                    return sensor.Value;
                case "fvalue": // (commonly) formatted value
                    return String.Format(sensor.GetSensorValueFormat(), sensor.Value);
                case "type":
                    return sensor.SensorType;
                case "unit":
                    return sensor.GetSensorUnit();
                default: return null;
            }
        }

        public static string FormatSensorString(this ISensor sensor, string format)
        {
            return Regex.Replace(format, @"{([^}]+)}", new MatchEvaluator(
                (Match match) =>
                {
                    var pack = match.Groups[1].Value;
                    var parts = pack.Split(new string[] { ":" }, StringSplitOptions.RemoveEmptyEntries);
                    string varName;
                    string entryFormat;
                    if (parts.Length <= 1)
                    {
                        varName = parts[0];
                        entryFormat = "{0}";
                    }
                    else
                    {
                        varName = parts[0];
                        entryFormat = $"{{0:{parts[1]}}}";
                    }
                    return String.Format(entryFormat, sensor.GetSensorAttribute(varName));
                }
            ));
        }
    }

    public class EditorSensorAttribute : Attribute
    {
        public List<ISensor> Sensors
        {
            get { return LCARSSystem.Global.GetAvailableSensors(); }
        }
    }

    public class EditorSensorEntry
    {
        public ISensor? Sensor { get; protected set; }
        public string? SensorID
        {
            get
            {
                if (Sensor == null)
                    return null;
                return Sensor.Identifier.ToString();
            }
        }
        public string DisplayName
        {
            get
            {
                if (Sensor == null)
                    return "None";
                return $"{Sensor.Hardware.Name} ({Sensor.SensorType}): {Sensor.Name}";
            }
        }

        public EditorSensorEntry(ISensor? sensor)
        {
            Sensor = sensor;
        }
    }
}
