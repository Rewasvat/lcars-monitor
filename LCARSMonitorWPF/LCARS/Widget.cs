using LibreHardwareMonitor.Hardware;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace LCARSMonitor.LCARS
{
    public class Widget
    {
        public WidgetSystem System { get; }
        public ISensor Sensor { get; }
        public WidgetVisitor Visitor { get; }
        public FrameworkElement? View
        {
            get { return Visitor.View; }
        }

        public Widget(WidgetSystem system, ISensor sensor, WidgetVisitor visitor)
        {
            System = system;
            Sensor = sensor;
            Visitor = visitor;
            visitor.Parent = this;
        }

        /// <summary>
        /// Updates this Widget, updating our Control with new data from our Sensor.
        /// This may update our associated Hardware (from our Sensor), if it wasn't updated yet.
        /// </summary>
        public void AsyncUpdate()
        {
            Sensor.Hardware.Accept(Visitor);
            Sensor.Accept(Visitor);
        }

        public void Update()
        {
            Visitor.Update();
        }
    }
}
