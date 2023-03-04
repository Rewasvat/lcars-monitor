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
        private Color NormalColor;
        private Color MouseOverColor;
        private Color PressedColor;
        private Color DisabledColor;

        public Color Normal
        {
            get { return NormalColor; }
            protected set
            {
                NormalBrush = new SolidColorBrush(value);
                NormalColor = value;
            }
        }
        public Color MouseOver
        {
            get { return MouseOverColor; }
            protected set
            {
                MouseOverBrush = new SolidColorBrush(value);
                MouseOverColor = value;
            }
        }
        public Color Pressed
        {
            get { return PressedColor; }
            protected set
            {
                PressedBrush = new SolidColorBrush(value);
                PressedColor = value;
            }
        }
        public Color Disabled
        {
            get { return DisabledColor; }
            protected set
            {
                DisabledBrush = new SolidColorBrush(value);
                DisabledColor = value;
            }
        }

        public SolidColorBrush NormalBrush { get; protected set; }
        public SolidColorBrush MouseOverBrush { get; protected set; }
        public SolidColorBrush PressedBrush { get; protected set; }
        public SolidColorBrush DisabledBrush { get; protected set; }

        public Visual()
        {
            NormalBrush = new SolidColorBrush(Colors.White);
            MouseOverBrush = new SolidColorBrush(Colors.White);
            PressedBrush = new SolidColorBrush(Colors.White);
            DisabledBrush = new SolidColorBrush(Colors.White);
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
