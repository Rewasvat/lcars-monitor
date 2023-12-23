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
    /// Interaction logic for RegularBar.xaml
    /// </summary>
    public partial class RegularBar : UserControl, IProgressBarStyle
    {
        public RegularBar()
        {
            InitializeComponent();
        }

        public void OnSensorUpdate(BarConfig config)
        {
        }

        public void OnConfigChanged(BarConfig config)
        {
        }
    }
}
