using System;
using System.Collections.Generic;
using System.Diagnostics;
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
using LCARSMonitor.LCARS;
using LCARSMonitorWPF.LCARS.Commands;
using LibreHardwareMonitor.Hardware;
using Newtonsoft.Json;

namespace LCARSMonitorWPF.Controls
{
    /// <summary>
    /// Interaction logic for Button.xaml
    /// </summary>
    public partial class Button : LCARSControl, ILCARSSensorHandler, ILCARSCommandContainer
    {
        // PROPERTIES
        [JsonProperty]
        public Stumps Stumps
        {
            get { return (Stumps)GetValue(StumpsProperty); }
            set { SetValue(StumpsProperty, value); }
        }
        public static readonly DependencyProperty StumpsProperty = DependencyProperty.Register(
            "Stumps",
            typeof(Stumps),
            typeof(Button),
            new PropertyMetadata(Stumps.Both, StumpsChanged)
        );
        private static void StumpsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            (d as Button)?.UpdateCorners();
        }

        [JsonProperty]
        public Visuals VisualStyle
        {
            get { return (Visuals)GetValue(VisualStyleProperty); }
            set { SetValue(VisualStyleProperty, value); }
        }
        public static readonly DependencyProperty VisualStyleProperty = DependencyProperty.Register(
            "VisualStyle",
            typeof(Visuals),
            typeof(Button),
            new PropertyMetadata(Visuals.Common, StyleChanged)
        );
        private static void StyleChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is Button obj)
            {
                obj.UpdateVisual();
            }
        }

        public Visual Visual
        {
            get { return Visual.GetVisual(VisualStyle); }
        }

        [JsonProperty]
        public string Label
        {
            get { return (string)GetValue(LabelProperty); }
            set { SetValue(LabelProperty, value); }
            // TODO: suportar mudar tamanho do texto?
            // TODO: poder mudar alinhamento do texto?
        }
        public static readonly DependencyProperty LabelProperty = DependencyProperty.Register(
            "Label",
            typeof(string),
            typeof(Button),
            new PropertyMetadata(string.Empty, LabelChanged)
        );
        private static void LabelChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is Button obj)
            {
                obj.UpdateLabel();
            }
        }

        [JsonProperty]
        public bool UseFixedVisual { get; set; } = false;

        public SensorBundle SensorBundle { get; protected set; }
        private string? attachedSensorId;
        [JsonProperty]
        [EditorSensor]
        public string? AttachedSensorId
        {
            get { return attachedSensorId; }
            set
            {
                attachedSensorId = value;
                if (value != null)
                    SensorBundle.SetSensors(new string[] { value });
                else
                {
                    SensorBundle.SetSensors(new string[] { });
                }
                UpdateLabel();
            }
        }

        [JsonProperty]
        [IgnoreOnEditor]
        public ILCARSCommand? OnClick
        {
            get { return Commands["OnClick"].Command; }
            set { Commands["OnClick"].Command = value; }
        }

        public Dictionary<string, CommandSlot> Commands { get; protected set; }

        // INTERNAL ATTRIBUTES
        private bool hasMouseOver = false;
        private bool isPressed = false;

        public Button()
        {
            InitializeComponent();
            rect.BorderBrush = null;
            rect.Background = Visual.NormalBrush;

            Commands = new Dictionary<string, CommandSlot>(1);
            Commands["OnClick"] = new CommandSlot("OnClick", this);

            UpdateVisual();
            UpdateCorners();

            SensorBundle = new SensorBundle(this);
        }

        protected void UpdateVisual()
        {
            var fill = Visual.NormalBrush;
            if (!UseFixedVisual)
            {
                if (!IsEnabled) fill = Visual.DisabledBrush;
                else if (isPressed) fill = Visual.PressedBrush;
                else if (hasMouseOver) fill = Visual.MouseOverBrush;
            }

            rect.Background = fill;
            label.Foreground = Visual.TextBrush;
            // TODO: fix issue: click, drag outside button and release. Button stays on "pressed" state even tho it isnt anymore
        }

        protected void UpdateCorners()
        {
            double radius = rect.ActualHeight / 2;
            switch (Stumps)
            {
                case Stumps.None:
                    rect.CornerRadius = new CornerRadius(0);
                    rect.Padding = new Thickness(5, 0, 5, 0);
                    break;
                case Stumps.Left:
                    rect.CornerRadius = new CornerRadius(radius, 0, 0, radius);
                    rect.Padding = new Thickness(radius, 0, 5, 0);
                    break;
                case Stumps.Right:
                    rect.CornerRadius = new CornerRadius(0, radius, radius, 0);
                    rect.Padding = new Thickness(5, 0, radius, 0);
                    break;
                case Stumps.Both:
                    rect.CornerRadius = new CornerRadius(radius);
                    rect.Padding = new Thickness(radius, 0, radius, 0);
                    break;
            }
        }

        protected void UpdateLabel()
        {
            string finalLabel = Label;
            if (AttachedSensorId != null)
            {
                // when a sensor is attached, the Label can be a format to include sensor data
                var sensor = SensorBundle.Sensors[AttachedSensorId];
                finalLabel = sensor.FormatSensorString(Label);
            }
            label.Content = finalLabel;
        }
        public void OnSensorUpdate(ISensor sensor)
        {
            // UpdateLabel gets the sensor itself instead of receiving from here since we also use that method in other places.
            UpdateLabel();
        }

        private void LCARSControl_IsEnabledChanged(object sender, DependencyPropertyChangedEventArgs e)
        {
            UpdateVisual();
        }

        private void LCARSControl_MouseEnter(object sender, MouseEventArgs e)
        {
            hasMouseOver = true;
            UpdateVisual();
        }
        private void LCARSControl_MouseLeave(object sender, MouseEventArgs e)
        {
            hasMouseOver = false;
            UpdateVisual();
        }

        private void LCARSControl_MouseDown(object sender, MouseButtonEventArgs e)
        {
            isPressed = true;
            UpdateVisual();
        }

        private void LCARSControl_MouseUp(object sender, MouseButtonEventArgs e)
        {
            isPressed = false;
            UpdateVisual();
            if (OnClick != null)
                OnClick.OnRun();
        }

        private void LCARSControl_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            // UpdateVisual();
            UpdateCorners();
        }
    }
}
