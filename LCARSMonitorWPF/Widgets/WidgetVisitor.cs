using LibreHardwareMonitor.Hardware;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace LCARSMonitor.Widgets
{
    public abstract class WidgetVisitor : IVisitor
    {
        public Widget? Parent { get; set; }
        public FrameworkElement? View { get; protected set; }

        public void VisitComputer(IComputer computer) { }
        public void VisitParameter(IParameter parameter) { }

        public void VisitHardware(IHardware hardware)
        {
            if (!Parent!.System.IsHardwareUpdated(hardware))
            {
                hardware.Update();
                Parent.System.MarkHardwareUpdated(hardware);
                foreach (IHardware subHardware in hardware.SubHardware)
                {
                    subHardware.Accept(this);
                }
            }
        }

        public virtual void VisitSensor(ISensor sensor)
        {
            // Inherit classes specialize with a WinForms Controls, they should implement this
            // to get sensor data and update the control
            throw new NotImplementedException();
        }

        public virtual void Update() { }

        public string GetSensorUnit(ISensor sensor)
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

        public string GetSensorValueFormat(ISensor sensor)
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

        public string FormatSensorString(ISensor sensor, string format)
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
                    return String.Format(entryFormat, GetSensorAttribute(sensor, varName));
                }
            ));
        }


        private object? GetSensorAttribute(ISensor sensor, string key)
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
                    return String.Format(GetSensorValueFormat(sensor), sensor.Value);
                case "type":
                    return sensor.SensorType;
                case "unit":
                    return GetSensorUnit(sensor);
                default: return null;
            }
        }
    }
}
