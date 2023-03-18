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
using LCARSMonitor.LCARS;
using LCARSMonitorWPF.Windows.Editor;

namespace LCARSMonitorWPF.Windows.Monitor
{
    /// <summary>
    /// Interaction logic for TrayMenu.xaml
    /// </summary>
    public partial class TrayMenu : ContextMenu
    {
        private EditorWindow? editor;

        public TrayMenu()
        {
            InitializeComponent();

            LCARSSystem.Global.InitializedEvent += OnSystemInitialized;
        }

        private void OnQuitClicked(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private void OnOpenEditorClicked(object sender, RoutedEventArgs e)
        {
            ShowEditor();
        }

        private void ShowEditor()
        {
            if (editor == null)
            {
                editor = new EditorWindow();
                editor.Show();
                editor.Closed += OnEditorClosed;
            }
        }

        private void OnSystemInitialized(object sender, EventArgs e)
        {
            if (LCARSSystem.Global.RootSlot?.AttachedChild == null)
            {
                ShowEditor();
            }
        }

        private void OnEditorClosed(object? sender, EventArgs e)
        {
            editor = null;
        }
    }
}
