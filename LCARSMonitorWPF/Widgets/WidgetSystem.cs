using LibreHardwareMonitor.Hardware;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;

namespace LCARSMonitor.Widgets
{
    public class WidgetSystem
    {
        private Computer computer;
        private List<Widget> widgets;
        private Dictionary<Identifier, bool> updatedHardwares;

        public Panel WidgetsPanel { get; private set; }

        public WidgetSystem(Panel widgetsPanel)
        {
            WidgetsPanel = widgetsPanel;
            widgets = new List<Widget>();
            updatedHardwares = new Dictionary<Identifier, bool>();

            computer = new Computer
            {
                IsCpuEnabled = true,
                IsGpuEnabled = true,
                IsMemoryEnabled = true,
                IsMotherboardEnabled = true,
                IsControllerEnabled = true,
                IsStorageEnabled = true,
                IsNetworkEnabled = true,
                IsBatteryEnabled = true,
                IsPsuEnabled = true,
            };

            // computer.HardwareAdded += WAT;
            // computer.HardwareRemoved += WAT;
            computer.Open();
        }

        /// <summary>
        /// Updates this Widget System, by updating all of our widgets.
        /// This in turn shall update all hardwares associated with our widgets, in order to update their sensor data.
        /// </summary>
        public void AsyncUpdate()
        {
            updatedHardwares.Clear();
            foreach (Widget widget in widgets)
            {
                widget.AsyncUpdate();
            }
        }

        public void Update()
        {
            foreach (Widget widget in widgets)
            {
                widget.Update();
            }
        }

        /// <summary>
        /// Resets our internal Computer
        /// </summary>
        public void Reset()
        {
            computer.Reset();
        }

        /// <summary>
        /// Disposes our internal Computer
        /// </summary>
        public void Dispose()
        {
            computer.Close();
        }

        /// <summary>
        /// Checks if the given hardware was already updated, in the current WidgetSystem Update cycle.
        /// This flag resets with each Update cycle, and is then updated by <see cref="Widget"/>/<see cref="WidgetVisitor"/>
        /// to ensure each hardware is only updated once.
        /// </summary>
        /// <param name="hardware">Hardware to check if was already updated</param>
        /// <returns>True if hardware was already updated, false otherwise</returns>
        public bool IsHardwareUpdated(IHardware hardware)
        {
            bool exists = updatedHardwares.TryGetValue(hardware.Identifier, out var value);
            return exists && value;
        }

        /// <summary>
        /// Sets the given hardware as being already updated in the current WidgetSystem Update cycle.
        /// </summary>
        /// <param name="hardware">The hardware to mark</param>
        public void MarkHardwareUpdated(IHardware hardware)
        {
            updatedHardwares.Add(hardware.Identifier, true);
        }

        /// <summary>
        /// Adds a new widget to the system.
        /// </summary>
        /// <param name="widget">new widget to be added</param>
        public void AddWidget(Widget widget)
        {
            widgets.Add(widget);
            WidgetsPanel.Children.Add(widget.View);
        }

        /// <summary>
        /// Gets a list of available sensors from the computer, across all hardwares.
        /// </summary>
        /// <returns>List of all sensors</returns>
        public List<ISensor> GetAvailableSensors()
        {
            List<ISensor> sensors = new List<ISensor>();

            // Dava pra implementar isso com um Visitor tb...
            foreach (IHardware hardware in computer.Hardware)
            {
                foreach (IHardware subhardware in hardware.SubHardware)
                {
                    foreach (ISensor sensor in subhardware.Sensors)
                    {
                        sensors.Add(sensor);
                    }
                }

                foreach (ISensor sensor in hardware.Sensors)
                {
                    sensors.Add(sensor);
                }
            }

            return sensors;
        }

        /// <summary>
        /// Gets a specific sensor by its ID from the list of available sensors.
        /// </summary>
        /// <param name="id">The sensor ID to check for. Should match Sensor.Identifier.ToString().</param>
        /// <returns>The sensor with the given ID or null.</returns>
        public ISensor? GetSensorByID(string id)
        {
            Identifier identifier = new Identifier(id.Split(new string[] { "/" }, StringSplitOptions.RemoveEmptyEntries));
            var sensors = GetAvailableSensors();
            foreach (ISensor sensor in sensors)
            {
                if (sensor.Identifier == identifier)
                {
                    return sensor;
                }
            }
            return null;
        }
    }
}
