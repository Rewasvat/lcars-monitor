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
        private Color TextColor;

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
        public Color Text
        {
            get { return TextColor; }
            protected set
            {
                TextBrush = new SolidColorBrush(value);
                TextColor = value;
            }
        }

        public SolidColorBrush NormalBrush { get; protected set; }
        public SolidColorBrush MouseOverBrush { get; protected set; }
        public SolidColorBrush PressedBrush { get; protected set; }
        public SolidColorBrush DisabledBrush { get; protected set; }
        public SolidColorBrush TextBrush { get; protected set; }

        public Visual()
        {
            NormalColor = Colors.White;
            NormalBrush = new SolidColorBrush(NormalColor);

            MouseOverColor = Colors.White;
            MouseOverBrush = new SolidColorBrush(MouseOverColor);

            PressedColor = Colors.White;
            PressedBrush = new SolidColorBrush(PressedColor);

            DisabledColor = FromHex("7f7f7f");
            DisabledBrush = new SolidColorBrush(DisabledColor);

            TextColor = Colors.Black;
            TextBrush = new SolidColorBrush(TextColor);
        }

        public static Color FromHex(string hex)
        {
            return (Color)ColorConverter.ConvertFromString("#FF" + hex);
        }

        public static Visual MainRed
        {
            get
            {
                var style = new Visual();
                style.Normal = FromHex("cc6666");
                style.MouseOver = FromHex("ab5555");
                return style;
            }
        }

        public static Visual MainPink
        {
            get
            {
                var style = new Visual();
                style.Normal = FromHex("e6b0d4");
                style.MouseOver = FromHex("bd92af");
                return style;
            }
        }

        public static Visual MainBlue
        {
            get
            {
                var style = new Visual();
                style.Normal = FromHex("99ccff");
                style.MouseOver = FromHex("85a8c5");
                return style;
            }
        }

        public static Visual LightBlue
        {
            get
            {
                var style = new Visual();
                style.Normal = FromHex("add8e6");
                style.MouseOver = FromHex("91b5c0");
                return style;
            }
        }

        public static Visual MainOrange
        {
            get
            {
                var style = new Visual();
                style.Normal = FromHex("ff9900");
                style.MouseOver = FromHex("cc7f16");
                return style;
            }
        }

        public static Visual MainYellow
        {
            get
            {
                var style = new Visual();
                style.Normal = FromHex("efb657");
                style.MouseOver = FromHex("c49749");
                return style;
            }
        }

        public static Visual MainBeige
        {
            get
            {
                var style = new Visual();
                style.Normal = FromHex("eeb683");
                style.MouseOver = FromHex("c4986d");
                return style;
            }
        }

        public static Visual MainGreen
        {
            get
            {
                var style = new Visual();
                style.Normal = FromHex("15a957");
                style.MouseOver = FromHex("088e48");
                return style;
            }
        }

        public static Visual ExternalLabel
        {
            get
            {
                var style = new Visual();
                style.Normal = style.MouseOver = style.Pressed = style.Disabled = Colors.Black;
                style.Text = FromHex("ff9900");  // same as MainOrange
                return style;
            }
        }


        public static Visual GetVisual(Visuals styles)
        {
            switch (styles)
            {
                case Visuals.Common: return MainYellow;
                case Visuals.MainRed: return MainRed;
                case Visuals.MainPink: return MainPink;
                case Visuals.MainBlue: return MainBlue;
                case Visuals.LightBlue: return LightBlue;
                case Visuals.MainOrange: return MainOrange;
                case Visuals.MainYellow: return MainYellow;
                case Visuals.MainBeige: return MainBeige;
                case Visuals.MainGreen: return MainGreen;
                case Visuals.ExternalLabel: return ExternalLabel;
                default: return MainYellow;
            }
        }
    }

    public enum Visuals
    {
        Common,
        MainRed,
        MainPink,
        MainBlue,
        LightBlue,
        MainOrange,
        MainYellow,
        MainBeige,
        MainGreen,
        ExternalLabel,
    }
}
