using Hardcodet.Wpf.TaskbarNotification;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace LCARSMonitorWPF
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        private TaskbarIcon? trayIcon;

        private void Application_Startup(object sender, StartupEventArgs e)
        {
            trayIcon = new TaskbarIcon();
            trayIcon.IconSource = new BitmapImage(new Uri("pack://application:,,,/Assets/Icons/lcars.png"));
            trayIcon.ToolTipText = "LCARS Monitor";
        }
    }
}
