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
        public Canvas ChildrenCanvas => canvas;

        public MonitorWindow()
        {
            InitializeComponent();

            ChildSlot = new Slot(this);
            UpdateRootSlot();

            RedAlert red = new RedAlert();
            AxisList list = new AxisList();
            list.Orientation = AxisOrientation.Vertical;
            list.Config = "1/1/1/1";
            list.ChildrenPadding = 7.0;

            Controls.Button red1 = new Controls.Button();
            red1.VisualStyle = Visuals.MainGreen;
            red1.Stumps = Stumps.Both;
            red1.Label = $"Test {typeof(Controls.Panel).FullName}";
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

            Controls.Panel panel = new Controls.Panel();
            panel.Borders = PanelBorders.Bottom | PanelBorders.Top | PanelBorders.Left;
            panel.ChildSlot.AttachedChild = list;

            Controls.RedAlert alert = new RedAlert();

            Controls.Board board = new Board();
            board.BoardNames = new string[] { "Main", "Alt" };
            board.CurrentBoard = "Main";
            board.Slots["Main"].AttachedChild = panel;
            board.Slots["Alt"].AttachedChild = alert;

            ChildSlot.AttachedChild = board;
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
