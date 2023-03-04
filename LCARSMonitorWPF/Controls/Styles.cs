using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media;

namespace LCARSMonitorWPF.Controls
{
    public class Visual
    {
        public Color Normal { get; set; }
        public Color MouseOver { get; set; }
        public Color Pressed { get; set; }
        public Color Disabled { get; set; }

        public Visual() { }

        public void SetAsFixedColor(Color color)
        {
            Normal = MouseOver = Pressed = Disabled = color;
        }

        public static Visual Common
        {
            get
            {
                var style = new Visual();
                style.Normal = Colors.Yellow;
                style.MouseOver = Colors.LightYellow;
                style.Pressed = Colors.Orange;
                style.Disabled = Colors.Red;
                return style;
            }
        }
        // TODO: criar outros styles padrão (implementar método padrão, valor na Enum, e switch-case no GetStyle)

        public static Visual GetVisual(Visuals styles)
        {
            switch (styles)
            {
                case Visuals.Common: return Common;
                default: return Common;
            }
        }
    }

    public enum Visuals
    {
        Common
    }
}
