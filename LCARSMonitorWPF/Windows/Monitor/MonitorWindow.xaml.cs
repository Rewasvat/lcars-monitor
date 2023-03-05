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
using LCARSMonitorWPF.Controls;

namespace LCARSMonitorWPF.Windows.Monitor
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MonitorWindow : Window
    {
        private Computer computer;
        private UpdateVisitor visitor = new UpdateVisitor();

        public MonitorWindow()
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

            // RedAlert red = new RedAlert();
            AxisList list = new AxisList();
            list.Orientation = AxisOrientation.Vertical;
            list.Config = "1/1/1/1";

            Controls.Button red1 = new Controls.Button();
            red1.VisualStyle = Visuals.MainGreen;
            red1.Stumps = Stumps.Both;
            red1.Label = "Test 1";
            list.ChildSlots[0].AttachedChild = red1;

            Controls.Button red2 = new Controls.Button();
            red2.VisualStyle = Visuals.MainOrange;
            red2.Stumps = Stumps.Both;
            red2.Label = "Test 2";
            list.ChildSlots[1].AttachedChild = red2;

            Controls.Button red3 = new Controls.Button();
            red3.VisualStyle = Visuals.MainPink;
            red3.Stumps = Stumps.Both;
            red3.Label = "Test 3";
            list.ChildSlots[2].AttachedChild = red3;

            Controls.Button red4 = new Controls.Button();
            red4.VisualStyle = Visuals.MainRed;
            red4.Stumps = Stumps.Both;
            red4.Label = "Test 4";
            list.ChildSlots[3].AttachedChild = red4;

            panel.ChildSlot.AttachedChild = list;
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
