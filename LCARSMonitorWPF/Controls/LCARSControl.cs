using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;

namespace LCARSMonitorWPF.Controls
{
    public abstract class LCARSControl : UserControl
    {
        public virtual void OnAttachToSlot(Slot? slot)
        {
            // NOTE: this assumes parent object is always a Canvas (this is true for Panel, but what about other containers?)
            if (slot != null)
            {
                IsEnabled = true;
                Visibility = System.Windows.Visibility.Visible;

                var rect = slot.Area;
                SetValue(Canvas.LeftProperty, rect.Left);
                SetValue(Canvas.TopProperty, rect.Top);
                Width = Math.Max(10, rect.Width);
                Height = Math.Max(10, rect.Height);
            }
            else
            {
                IsEnabled = true;
                Visibility = System.Windows.Visibility.Hidden;
            }
        }
    }
}
