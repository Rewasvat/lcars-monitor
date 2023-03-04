using LibreHardwareMonitor.Hardware;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace LCARSMonitorWPF
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private Computer computer;
        private UpdateVisitor visitor = new UpdateVisitor();

        public MainWindow()
        {
            InitializeComponent();

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

            //// computer.HardwareAdded += WAT;
            //// computer.HardwareRemoved += WAT;
            //computer.Open();

            //computer.Accept(visitor);

            //string msg = "";
            //foreach (IHardware hardware in computer.Hardware)
            //{
            //    msg += $"Hardware '{hardware.Name}'\n";
            //    foreach (IHardware subhardware in hardware.SubHardware)
            //    {
            //        msg += $"   * SubHardware '{hardware.Name}'\n";
            //        foreach (ISensor sensor in subhardware.Sensors)
            //        {
            //            msg += $"      * Sensor '{sensor.Name}'\n";
            //        }
            //    }
            //    foreach (ISensor sensor in hardware.Sensors)
            //    {
            //        msg += $"   * Sensor '{sensor.Name}': {sensor.Value} {sensor.SensorType}\n";
            //    }
            //}

            //computer.Close();

            //labelStuff.Content = msg;
        }
    }

    public class UpdateVisitor : IVisitor
    {
        public void VisitComputer(IComputer computer)
        {
            computer.Traverse(this);
        }

        public void VisitHardware(IHardware hardware)
        {
            hardware.Update();
            foreach (IHardware subHardware in hardware.SubHardware)
                subHardware.Accept(this);
        }

        public void VisitSensor(ISensor sensor) { }

        public void VisitParameter(IParameter parameter) { }
    }
}
