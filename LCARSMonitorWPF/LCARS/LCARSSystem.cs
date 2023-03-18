using LibreHardwareMonitor.Hardware;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;
using LCARSMonitorWPF.Properties;
using LCARSMonitorWPF.Controls;
using System.ComponentModel;
using System.Windows.Threading;
using System.Configuration;
using Newtonsoft.Json;
using System.IO;

namespace LCARSMonitor.LCARS
{
    public class LCARSSystem
    {
        private static LCARSSystem? global;
        public static LCARSSystem Global
        {
            get
            {
                if (global == null)
                    global = new LCARSSystem();
                return global;
            }
        }
        private static string SettingsFilePath = "LCARSSettings.json";

        private Computer computer;
        private Dictionary<Identifier, bool> updatedHardwares;
        private Dictionary<string, ISensor> allSensors;
        private Dictionary<string, LCARSControl> controls;
        private DispatcherTimer timer;
        private BackgroundWorker worker;
        private int unnamedControlsCount = 0;
        private SystemSettings settings;

        public Canvas? RootCanvas { get; private set; }
        public Slot? RootSlot { get; private set; }

        public delegate void InitializedEventHandler(object sender, EventArgs x);
        public event InitializedEventHandler? InitializedEvent;

        private LCARSSystem()
        {
            updatedHardwares = new Dictionary<Identifier, bool>();
            allSensors = new Dictionary<string, ISensor>();
            controls = new Dictionary<string, LCARSControl>();
            timer = new DispatcherTimer();
            worker = new BackgroundWorker();

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

            settings = new SystemSettings();
        }

        public void Initialize(Canvas root, Slot slot)
        {
            RootCanvas = root;
            RootSlot = slot;

            // computer.HardwareAdded += WAT;
            // computer.HardwareRemoved += WAT;
            computer.Open();

            timer.Interval = new TimeSpan(0, 0, 1);
            timer.Tick += Timer_Tick;
            timer.Start();

            worker.DoWork += worker_DoWork;
            worker.RunWorkerCompleted += worker_RunWorkerCompleted;

            Microsoft.Win32.SystemEvents.PowerModeChanged += SystemEvents_PowerModeChanged;
            Microsoft.Win32.SystemEvents.SessionEnded += SystemEvents_SessionEnded;

            foreach (ISensor sensor in GetAvailableSensors())
            {
                allSensors[sensor.Identifier.ToString()] = sensor;
            }

            if (File.Exists(SettingsFilePath))
            {
                using (StreamReader file = File.OpenText(SettingsFilePath))
                {
                    JsonSerializer serializer = new JsonSerializer();
                    settings = (SystemSettings)serializer.Deserialize(file, typeof(SystemSettings))!;
                }
            }

            RootSlot.AttachedChild = LoadControl(settings.CurrentRootControl);

            InitializedEvent?.Invoke(this, new EventArgs());
        }

        /// <summary>
        /// Updates this Widget System, by updating all of our widgets.
        /// This in turn shall update all hardwares associated with our widgets, in order to update their sensor data.
        /// </summary>
        public void AsyncUpdate()
        {
            updatedHardwares.Clear();

            foreach (var control in controls.Values)
            {
                ILCARSSensorHandler? handler = control as ILCARSSensorHandler;
                if (handler != null)
                {
                    handler.SensorBundle.AsyncUpdate();
                }
            }
        }

        public void Update()
        {
            foreach (var control in controls.Values)
            {
                ILCARSSensorHandler? handler = control as ILCARSSensorHandler;
                if (handler != null)
                {
                    handler.SensorBundle.Update();
                }
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

        public void Save()
        {
            if (RootSlot != null && RootSlot.AttachedChild != null)
            {
                settings.CurrentRootControl = RootSlot.AttachedChild.ID;
                SaveControl(RootSlot.AttachedChild);
            }

            using (StreamWriter file = File.CreateText(SettingsFilePath))
            {
                using (JsonTextWriter jw = new JsonTextWriter(file))
                {
                    jw.Formatting = Formatting.Indented;
                    jw.IndentChar = ' ';
                    jw.Indentation = 4;

                    JsonSerializer serializer = new JsonSerializer();
                    serializer.Serialize(jw, settings);
                }
            }
        }

        public void Shutdown()
        {
            Dispose();
            Save();
            timer.Stop();
            worker.Dispose();
        }

        /// <summary>
        /// Checks if the given hardware was already updated, in the current WidgetSystem Update cycle.
        /// This flag resets with each Update cycle, and is then updated by <see cref="Widget"/>/<see cref="SensorBundle"/>
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
        /// Registers a new LCARSControl to the system.
        /// </summary>
        /// <param name="control">new control to be registered</param>
        internal void RegisterControl(LCARSControl control)
        {
            if (control.ID == null || control.ID == "")
            {
                control.ID = $"UnnamedControl{unnamedControlsCount++}";
            }
            else
            {
                controls[control.ID] = control;
            }
        }

        internal void UpdateControlID(LCARSControl control, string newId)
        {
            controls.Remove(control.ID);
            control.Name = newId;
            controls[newId] = control;
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
            // Identifier identifier = new Identifier(id.Split(new string[] { "/" }, StringSplitOptions.RemoveEmptyEntries));
            if (allSensors.ContainsKey(id))
                return allSensors[id];
            return null;
        }

        /// <summary>
        /// Gets an array of specific sensors by their IDs from the list of available sensors.
        /// </summary>
        /// <param name="ids">The sensor IDs to check for. Should match Sensor.Identifier.ToString().
        /// IDs that do not match sensors are ignored.</param>
        /// <returns>The array of sensors with the given IDs.</returns>
        public List<ISensor> GetSensorsByIDs(string[] ids)
        {
            var sensors = GetAvailableSensors();
            var result = new List<ISensor>(ids.Length);
            foreach (string id in ids)
            {
                ISensor? sensor = GetSensorByID(id);
                if (sensor != null)
                {
                    result.Add(sensor);
                }
            }
            return result;
        }

        public LCARSControl? GetControlByName(string name)
        {
            return controls.GetValueOrDefault(name);
        }

        public void SaveControl(LCARSControl control)
        {
            var controlPath = BuildControlFilePath(control);
            settings.ControlFilePaths[control.ID] = controlPath;
            Directory.CreateDirectory("UserControls");
            control.SerializeIntoJsonFile(controlPath);
        }

        public LCARSControl? LoadControl(string name)
        {
            if (!settings.ControlFilePaths.ContainsKey(name))
                return null;
            var controlPath = settings.ControlFilePaths[name];
            return LCARSControl.DeserializeJsonFile(controlPath);
        }

        private string BuildControlFilePath(LCARSControl control)
        {
            return $"UserControls/Control_{control.ID}.json";
        }

        public List<string> GetSavedControlNames()
        {
            return settings.ControlFilePaths.Keys.ToList<string>();
        }

        // EVENT CALLBACKS
        private void Timer_Tick(object? sender, EventArgs e)
        {
            if (!worker.IsBusy)
            {
                worker.RunWorkerAsync();
            }
        }

        private void worker_DoWork(object? sender, DoWorkEventArgs e)
        {
            AsyncUpdate();
        }

        private void worker_RunWorkerCompleted(object? sender, RunWorkerCompletedEventArgs e)
        {
            Update();
        }

        private void SystemEvents_PowerModeChanged(object sender, Microsoft.Win32.PowerModeChangedEventArgs e)
        {

            if (e.Mode == Microsoft.Win32.PowerModes.Resume)
            {
                Reset();
            }
        }

        private void SystemEvents_SessionEnded(object sender, Microsoft.Win32.SessionEndedEventArgs e)
        {
            Dispose();
            // TODO: save settings/config
        }
    }

    public class SystemSettings
    {
        public Dictionary<string, string> ControlFilePaths { get; set; } = new Dictionary<string, string>();
        public string CurrentRootControl { get; set; } = "";
    }
}
