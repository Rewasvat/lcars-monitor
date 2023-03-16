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
using LCARSMonitorWPF.LCARS.Commands;
using Newtonsoft.Json;

namespace LCARSMonitorWPF.Controls
{
    /// <summary>
    /// Interaction logic for Communicator.xaml
    /// </summary>
    public partial class Communicator : LCARSControl, ILCARSCommandContainer
    {
        public Dictionary<string, CommandSlot> Commands { get; protected set; }

        [JsonProperty]
        [IgnoreOnEditor]
        public ILCARSCommand? OnClick
        {
            get { return Commands["OnClick"].Command; }
            set { Commands["OnClick"].Command = value; }
        }

        // METHODS
        public Communicator()
        {
            InitializeComponent();

            Commands = new Dictionary<string, CommandSlot>(1);
            Commands["OnClick"] = new CommandSlot("OnClick", this);
        }

        private void OnMouseUp(object sender, MouseButtonEventArgs e)
        {
            if (OnClick != null)
                OnClick.OnRun();
        }
    }
}
