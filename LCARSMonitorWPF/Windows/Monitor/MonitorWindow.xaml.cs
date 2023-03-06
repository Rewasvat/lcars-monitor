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
using System.Diagnostics;
using Newtonsoft.Json;

namespace LCARSMonitorWPF.Windows.Monitor
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MonitorWindow : Window, ILCARSSingleContainer
    {
        public Slot ChildSlot { get; protected set; }

        public MonitorWindow()
        {
            InitializeComponent();

            ChildSlot = new Slot(this);
            UpdateRootSlot();

            // RedAlert red = new RedAlert();
            // AxisList list = new AxisList();
            // list.Orientation = AxisOrientation.Vertical;
            // list.Config = "1/1/1/1";

            // Controls.Button red1 = new Controls.Button();
            // red1.VisualStyle = Visuals.MainGreen;
            // red1.Stumps = Stumps.Both;
            // red1.Label = $"Test {typeof(Controls.Panel).FullName}";
            // list.ChildSlots[0].AttachedChild = red1;

            // Controls.Button red2 = new Controls.Button();
            // red2.VisualStyle = Visuals.MainOrange;
            // red2.Stumps = Stumps.Both;
            // red2.Label = "Test 2";
            // list.ChildSlots[1].AttachedChild = red2;

            // Controls.Button red3 = new Controls.Button();
            // red3.VisualStyle = Visuals.MainPink;
            // red3.Stumps = Stumps.Both;
            // red3.Label = "Test 3";
            // list.ChildSlots[2].AttachedChild = red3;

            // Controls.Button red4 = new Controls.Button();
            // red4.VisualStyle = Visuals.MainRed;
            // red4.Stumps = Stumps.Both;
            // red4.Label = "Test 4";
            // list.ChildSlots[3].AttachedChild = red4;

            // Controls.Panel panel = new Controls.Panel();
            // panel.Borders = PanelBorders.Bottom | PanelBorders.Top | PanelBorders.Left;
            // panel.ChildSlot.AttachedChild = list;

            /////
            // var data = panel.Serialize();

            // string jsonData = JsonConvert.SerializeObject(data, Formatting.Indented, new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.All });
            // Debug.WriteLine(jsonData);

            string jsonData = @"{
  '$type': 'LCARSMonitorWPF.Controls.PanelData, LCARSMonitorWPF',
  'VisualStyle': 0,
  'Borders': 13,
  'BorderHeight': 50.0,
  'BorderWidth': 200.0,
  'BorderInnerRadius': 30.0,
  'Content': {
    '$type': 'LCARSMonitorWPF.Controls.AxisListData, LCARSMonitorWPF',
    'Orientation': 1,
    'Config': '1/1/1/1',
    'Children': {
      '$type': 'LCARSMonitorWPF.Controls.LCARSControlData[], LCARSMonitorWPF',
      '$values': [
        {
          '$type': 'LCARSMonitorWPF.Controls.ButtonData, LCARSMonitorWPF',
          'UseFixedVisual': false,
          'Label': 'Test LCARSMonitorWPF.Controls.Panel',
          'VisualStyle': 8,
          'Stumps': 3,
          'Type': 'LCARSMonitorWPF.Controls.Button'
        },
        {
          '$type': 'LCARSMonitorWPF.Controls.ButtonData, LCARSMonitorWPF',
          'UseFixedVisual': false,
          'Label': 'Test 2',
          'VisualStyle': 5,
          'Stumps': 3,
          'Type': 'LCARSMonitorWPF.Controls.Button'
        },
        {
          '$type': 'LCARSMonitorWPF.Controls.ButtonData, LCARSMonitorWPF',
          'UseFixedVisual': false,
          'Label': 'Test 3',
          'VisualStyle': 2,
          'Stumps': 3,
          'Type': 'LCARSMonitorWPF.Controls.Button'
        },
        {
          '$type': 'LCARSMonitorWPF.Controls.ButtonData, LCARSMonitorWPF',
          'UseFixedVisual': false,
          'Label': 'Test 4 SUA BUNDA',
          'VisualStyle': 1,
          'Stumps': 3,
          'Type': 'LCARSMonitorWPF.Controls.Button'
        }
      ]
    },
    'Type': 'LCARSMonitorWPF.Controls.AxisList'
  },
  'Type': 'LCARSMonitorWPF.Controls.Panel'
}";
            LCARSControlData? newData = JsonConvert.DeserializeObject(jsonData, new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.All }) as LCARSControlData;

            Controls.Panel? newPanel = LCARSControl.Deserialize(newData) as Controls.Panel;
            /////

            // panel.Visibility = Visibility.Hidden;

            ChildSlot.AttachedChild = newPanel;
        }

        public void UpdateChildSlot(Slot slot, LCARSControl? newChild)
        {
            if (slot != ChildSlot)
            {
                // throw error?
                throw new ArgumentException("Tried to update a slot that is not our child slot", "slot");
            }

            if (slot.AttachedChild != null)
                canvas.Children.Remove(slot.AttachedChild);  // removing previous child
            if (newChild != null)
                canvas.Children.Add(newChild);
        }

        private void UpdateRootSlot()
        {
            var rect = ChildSlot.Area;
            rect.X = 0;
            rect.Y = 0;
            rect.Width = Math.Max(10, canvas.ActualWidth);
            rect.Height = Math.Max(10, canvas.ActualHeight);
            ChildSlot.Area = rect;
        }

        private void OnSizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateRootSlot();
        }
    }
}
