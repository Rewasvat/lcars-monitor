using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LCARSMonitorWPF.Controls
{
    public enum Stumps
    {
        None, Left, Right, Both
    }

    public enum ElbowType
    {
        TopLeft, TopRight, BottomRight, BottomLeft
    }

    [Flags]
    [TypeConverter(typeof(EnumConverter))]
    public enum PanelBorders
    {
        None = 0,
        Top = 1,
        Right = 2,
        Bottom = 4,
        Left = 8,
    }

    public enum AxisOrientation
    {
        Horizontal,
        Vertical
    }
}
