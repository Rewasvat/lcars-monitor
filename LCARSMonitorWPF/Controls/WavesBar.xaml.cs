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

namespace LCARSMonitorWPF.Controls
{
    /// <summary>
    /// Interaction logic for WavesBar.xaml
    /// </summary>
    public partial class WavesBar : UserControl, IProgressBarStyle
    {
        private SolidColorBrush markerBrush;
        private Thickness upMaxMarkerMargin;
        private Thickness upMinMarkerMargin;
        private Thickness downMaxMarkerMargin;
        private Thickness downMinMarkerMargin;
        private Dictionary<string, BarConfig?> lastConfigs;

        public WavesBar()
        {
            InitializeComponent();

            lastConfigs = new Dictionary<string, BarConfig?>()
            {
                ["Top"] = null,
                ["Bottom"] = null,
            };

            markerBrush = new SolidColorBrush(Colors.Red);
            upMaxMarkerMargin = new Thickness();
            upMinMarkerMargin = new Thickness();
            downMaxMarkerMargin = new Thickness();
            downMinMarkerMargin = new Thickness();

            upMaxMarker.Margin = upMaxMarkerMargin;
            upMinMarker.Margin = upMinMarkerMargin;
            downMaxMarker.Margin = downMaxMarkerMargin;
            downMinMarker.Margin = downMinMarkerMargin;
            // Background color:
            // HEX #add8e6
            // RGB 173 216 230
            //
            // RenderTransformOrigin = 0.5,0.5
            //
            // Stats: size=32x402.1
            // Up Elements: verticalAlign=Bottom horizontalAlign=Left (X)leftMargin=1 (Y)bottomMargin=22.1
            // Down Elemts: verticalAlign=Bottom horizontalAlign=Right (X)rightMargin=1 (Y)bottomMargin=22.1
        }

        public void OnSensorUpdate(BarConfig config)
        {
            if (!UpdateBar(config, config.Name))
            {
                // If updating bar with this config failed, it means config is "void" (has no sensor to show).
                // In this case, the bar should be mirrored - show only one sensor on both sides at the same time.
                // So we get the last config used by the opposite side, and use it on this side as well.
                var oppositeName = (config.Name == "Top") ? "Bottom" : "Top";
                var oppositeConfig = lastConfigs[oppositeName];
                if (oppositeConfig != null)
                    UpdateBar(oppositeConfig, config.Name);
            }
        }

        public void OnConfigChanged(BarConfig config)
        {
            OnSensorUpdate(config);
        }

        private bool UpdateBar(BarConfig config, string name)
        {
            if (config.Sensor == null)
                return false;

            var bg = GetBgBorder(name);
            var bar = GetBarBorder(name);

            bar.Height = bg.Height * config.CalculatePercentInRange(config.Sensor.Value);

            // TODO: suportar config.ValueLabel
            // TODO: suportar config.RangeLabel

            // Handle Marker
            var maxMarker = GetMaxMarker(name);
            var minMarker = GetMinMarker(name);
            if (config.UseMarker)
            {
                maxMarker.Fill = markerBrush;
                minMarker.Fill = markerBrush;

                if (name == "Top")
                {
                    upMaxMarkerMargin.Bottom = bg.Margin.Bottom + bg.Height * config.CalculatePercentInRange(config.Sensor.Max);
                    upMinMarkerMargin.Bottom = (bg.Margin.Bottom - minMarker.Height) + bg.Height * config.CalculatePercentInRange(config.Sensor.Min);
                    upMaxMarker.Margin = upMaxMarkerMargin;
                    upMinMarker.Margin = upMinMarkerMargin;
                }
                else
                {
                    // NOTE: at first this entire logic of WavesBar (all in this class) is essentially the same as in the ReactorBar.
                    // Basically only difference is this: here, downMarkers use Bottom margin for positioning, as well as the upMarkers
                    // However in ReactorBar, upMarkers use Bottom, while downMarkers use Top margin.
                    // TODO: might be better if we refactor this logic somewhere else to reuse in this WavesBar and in ReactorBar
                    downMaxMarkerMargin.Bottom = bg.Margin.Bottom + bg.Height * config.CalculatePercentInRange(config.Sensor.Max);
                    downMinMarkerMargin.Bottom = (bg.Margin.Bottom - minMarker.Height) + bg.Height * config.CalculatePercentInRange(config.Sensor.Min);
                    downMaxMarker.Margin = downMaxMarkerMargin;
                    downMinMarker.Margin = downMinMarkerMargin;
                }
            }
            else
            {
                maxMarker.Fill = null;
                minMarker.Fill = null;
            }

            lastConfigs[name] = config;

            return true;
        }

        private Border GetBgBorder(string name)
        {
            if (name == "Top")
            {
                return bgUp;
            }
            return bgDown;
        }
        private Border GetBarBorder(string name)
        {
            if (name == "Top")
            {
                return barUp;
            }
            return barDown;
        }

        private Path GetMaxMarker(string name)
        {
            if (name == "Top")
            {
                return upMaxMarker;
            }
            return downMaxMarker;
        }
        private Path GetMinMarker(string name)
        {
            if (name == "Top")
            {
                return upMinMarker;
            }
            return downMinMarker;
        }
    }
}
