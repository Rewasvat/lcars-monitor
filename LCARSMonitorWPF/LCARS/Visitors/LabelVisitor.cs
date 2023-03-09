using LibreHardwareMonitor.Hardware;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;

namespace LCARSMonitor.LCARS.Visitors
{
    public class LabelVisitor : WidgetVisitor
    {
        private Label label;
        private string format;
        private string textData = "no-data";

        public LabelVisitor(string format)
        {
            this.format = format;
            label = new Label();
            label.IsEnabled = true;
            label.Content = textData;
            View = label;
        }

        public LabelVisitor() : this("{value}") { }

        public override void VisitSensor(ISensor sensor)
        {
            textData = FormatSensorString(sensor, format);
        }

        public override void Update()
        {
            label.Content = textData;
        }
    }
}
