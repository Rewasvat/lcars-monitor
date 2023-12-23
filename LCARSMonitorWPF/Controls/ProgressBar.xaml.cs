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
using LCARSMonitor.LCARS;
using LibreHardwareMonitor.Hardware;
using Newtonsoft.Json;

namespace LCARSMonitorWPF.Controls
{
    /// <summary>
    /// Interaction logic for ProgressBar.xaml
    /// </summary>
    public partial class ProgressBar : LCARSControl, ILCARSSensorHandler
    {
        public SensorBundle SensorBundle { get; protected set; }

        private AxisOrientation orientation = AxisOrientation.Vertical;
        [JsonProperty]
        public AxisOrientation Orientation
        {
            get { return orientation; }
            set { orientation = value; UpdateOrientation(); }
        }

        private BarStyles barStyle = BarStyles.Reactor;
        [JsonProperty]
        public BarStyles BarStyle
        {
            get { return barStyle; }
            set
            {
                if (barStyle != value)
                {
                    barStyle = value;
                    CreateInternalBar();
                    UpdateContents(topConfig);
                    UpdateContents(bottomConfig);
                }
            }
        }

        private BarConfig topConfig;
        public BarConfig TopConfig { get { return topConfig; } }

        private BarConfig bottomConfig;
        public BarConfig BottomConfig { get { return bottomConfig; } }
        /* TODO FEATURES
        - selecionar cor do fundo?
        - setar valor min/max possivel da barra (tb poder pegar isso dos valores criticos do Sensor)
        - poder ligar (ou definir?) marker na barra de valor min/max registrado
        - poder definir label de valor atual (com FormatSensor)
        - poder definir label de min/max? (valor min/max ou min/max da barra?)
        - poder definir estilo visual da barra
            * estilo define o visual, e como certos elementos funcionam (marker, onde fica as labels, onde fica a barra em si, etc)
            * bom definir métodos de como setar conteudo nas sub-classes de barra... Seria bom fazer uma interface disso
        */

        private IProgressBarStyle? internalBar;

        private RotateTransform verticalRotation = new RotateTransform(0);
        private RotateTransform horizontalRotation = new RotateTransform(90);


        // METHODS

        public ProgressBar()
        {
            InitializeComponent();
            SensorBundle = new SensorBundle(this);
            topConfig = new BarConfig(this, "Top");
            bottomConfig = new BarConfig(this, "Bottom");

            CreateInternalBar();
            UpdateAllContent();
        }

        public void UpdateSensors()
        {
            if (topConfig.SensorId != null && bottomConfig.SensorId != null)
                SensorBundle.SetSensors(new string[] { topConfig.SensorId, bottomConfig.SensorId });
            else if (topConfig.SensorId != null)
                SensorBundle.SetSensors(new string[] { topConfig.SensorId });
            else if (bottomConfig.SensorId != null)
                SensorBundle.SetSensors(new string[] { bottomConfig.SensorId });
            else
                SensorBundle.SetSensors(new string[] { });

            internalBar?.OnSensorUpdate(topConfig);
            internalBar?.OnSensorUpdate(bottomConfig);
        }

        private void CreateInternalBar()
        {
            // Remove previous bar, if any
            if (internalBar != null)
            {
                canvas.Children.Remove(internalBar as UserControl);
            }

            // Create new bar
            if (BarStyle == BarStyles.Reactor)
            {
                internalBar = new ReactorBar();
            }
            else if (BarStyle == BarStyles.Waves)
            {
                internalBar = new WavesBar();
            }
            else if (BarStyle == BarStyles.Regular)
            {
                internalBar = new RegularBar();
            }
            else
            {
                internalBar = new RegularBar();
            }

            // Setup new bar
            UserControl bar = (UserControl)internalBar;
            canvas.Children.Add(bar);
            bar.HorizontalAlignment = HorizontalAlignment.Stretch;
            bar.VerticalAlignment = VerticalAlignment.Stretch;
            UpdateInternalBarSize();
        }

        private void UpdateInternalBarSize()
        {
            if (internalBar is UserControl bar)
            {
                bar.SetValue(Canvas.LeftProperty, 0.0);
                bar.SetValue(Canvas.TopProperty, 0.0);
                bar.Width = Width;
                bar.Height = Height;
            }
        }

        private void UpdateAllContent()
        {
            UpdateOrientation();
            UpdateContents(topConfig);
            UpdateContents(bottomConfig);
        }

        public void UpdateContents(BarConfig config)
        {
            if (config != topConfig && config != bottomConfig)
                return;

            internalBar?.OnConfigChanged(config);
        }

        private void UpdateOrientation()
        {
            if (internalBar is UserControl control)
            {
                if (Orientation == AxisOrientation.Vertical)
                    control.RenderTransform = verticalRotation;
                else if (Orientation == AxisOrientation.Horizontal)
                    control.RenderTransform = horizontalRotation;
            }
        }

        // EVENTS

        public void OnSensorUpdate(ISensor sensor)
        {
            if (sensor.Identifier.ToString() == topConfig.SensorId)
            {
                internalBar?.OnSensorUpdate(topConfig);
            }
            else if (sensor.Identifier.ToString() == bottomConfig.SensorId)
            {
                internalBar?.OnSensorUpdate(bottomConfig);
            }
        }

        private void OnSizeChanged(object sender, SizeChangedEventArgs e)
        {
            // ????
            UpdateInternalBarSize();
            UpdateContents(topConfig);
            UpdateContents(bottomConfig);
        }
    }

    public interface IProgressBarStyle
    {
        public void OnSensorUpdate(BarConfig config);
        public void OnConfigChanged(BarConfig config);
    }

    public class BarConfig
    {
        // Config Properties
        private string? sensorId;
        public string? SensorId
        {
            get { return sensorId; }
            set { sensorId = value; OnSensorChanged(); }
        }

        private BarLimitsRange limits = BarLimitsRange.SensorValueRange;
        public BarLimitsRange Limits
        {
            get { return limits; }
            set { limits = value; OnConfigChanged(); }
        }

        private double maxLimit = 100.0;
        public double MaxLimit
        {
            get { return maxLimit; }
            set { maxLimit = value; OnConfigChanged(); }
        }

        private double minLimit = 0.0;
        public double MinLimit
        {
            get { return minLimit; }
            set { minLimit = value; OnConfigChanged(); }
        }

        private string? valueLabel;
        public string? ValueLabel
        {
            get { return valueLabel; }
            set { valueLabel = value; OnConfigChanged(); }
        }

        private string? rangeLabel;
        public string? RangeLabel
        {
            get { return rangeLabel; }
            set { rangeLabel = value; OnConfigChanged(); }
        }

        private bool useMarker = false;
        public bool UseMarker
        {
            get { return useMarker; }
            set { useMarker = value; OnConfigChanged(); }
        }

        // Internal Properties
        public ProgressBar Parent { get; set; }
        public string Name { get; }
        public ISensor? Sensor
        {
            get
            {
                if (sensorId != null && Parent.SensorBundle.Sensors.ContainsKey(sensorId))
                    return Parent.SensorBundle.Sensors[sensorId];
                return null;
            }
        }

        // CONSTRUCTOR
        public BarConfig(ProgressBar parent, string name)
        {
            Parent = parent;
            Name = name;
        }

        // EVENTS
        private void OnSensorChanged()
        {
            Parent.UpdateSensors();
        }
        private void OnConfigChanged()
        {
            Parent.UpdateContents(this);
        }

        // METHODS
        public double CalculatePercentInRange(float? value)
        {
            // Calcula a porcentagem (de 0 a 1) do valor do sensor pra mostrar nessa barra, então leva em consideração os limites e tal
            // um control depois só precisaria transformar essa porcentagem num tamanho (percent*maxSize) pra atualizar o visual
            if (value == null)
                return 0.0;

            double min = GetRangeMin();
            double max = GetRangeMax();
            double range = max - min;
            if (range == 0.0)
                return 0.0;

            double factor = ((double)value - min) / range;
            return Math.Clamp(factor, 0.0, 1.0);
        }

        public double GetRangeMax()
        {
            double value = maxLimit; // User-defined limit is used as a default
            switch (limits)
            {
                case BarLimitsRange.SensorCritical:
                    if (Sensor is ICriticalSensorLimits criticalLimits)
                    {
                        value = criticalLimits.CriticalHighLimit != null ? (double)criticalLimits.CriticalHighLimit : value;
                    }
                    break;
                case BarLimitsRange.SensorLimits:
                    if (Sensor is ISensorLimits sensorLimits)
                    {
                        value = sensorLimits.HighLimit != null ? (double)sensorLimits.HighLimit : value;
                    }
                    break;
                case BarLimitsRange.SensorValueRange:
                    value = Sensor?.Max != null ? (double)Sensor.Max : value;
                    break;
                case BarLimitsRange.UserDefined:
                default:
                    break;
            }
            return value;
        }
        public double GetRangeMin()
        {
            double value = minLimit; // User-defined limit is used as a default
            switch (limits)
            {
                case BarLimitsRange.SensorCritical:
                    if (Sensor is ICriticalSensorLimits criticalLimits)
                    {
                        value = criticalLimits.CriticalLowLimit != null ? (double)criticalLimits.CriticalLowLimit : value;
                    }
                    break;
                case BarLimitsRange.SensorLimits:
                    if (Sensor is ISensorLimits sensorLimits)
                    {
                        value = sensorLimits.LowLimit != null ? (double)sensorLimits.LowLimit : value;
                    }
                    break;
                case BarLimitsRange.SensorValueRange:
                    value = Sensor?.Min != null ? (double)Sensor.Min : value;
                    break;
                case BarLimitsRange.UserDefined:
                default:
                    break;
            }
            return value;
        }
    }
}
