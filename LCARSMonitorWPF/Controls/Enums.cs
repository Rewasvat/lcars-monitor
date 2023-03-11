using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace LCARSMonitorWPF.Controls
{
    [JsonConverter(typeof(StringEnumConverter))]
    public enum Stumps
    {
        None, Left, Right, Both
    }

    [JsonConverter(typeof(StringEnumConverter))]
    public enum ElbowType
    {
        TopLeft, TopRight, BottomRight, BottomLeft
    }

    [Flags]
    [TypeConverter(typeof(EnumConverter))]
    [JsonConverter(typeof(StringEnumConverter))]
    public enum PanelBorders
    {
        None = 0,
        Top = 1,
        Right = 2,
        Bottom = 4,
        Left = 8,
    }

    [JsonConverter(typeof(StringEnumConverter))]
    public enum AxisOrientation
    {
        Horizontal,
        Vertical
    }
}
