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
using LCARSMonitorWPF.Windows.Editor;

namespace LCARSMonitorWPF.Windows.Monitor
{
    /// <summary>
    /// Interaction logic for TrayMenu.xaml
    /// </summary>
    public partial class TrayMenu : ContextMenu
    {
        public TrayMenu()
        {
            InitializeComponent();
        }

        private void OnQuitClicked(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private void OnOpenEditorClicked(object sender, RoutedEventArgs e)
        {
            EditorWindow editor = new EditorWindow();
            editor.Show();
        }
    }
}
