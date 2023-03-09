using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;

namespace LCARSMonitorWPF.LCARS.Commands
{
    public class SystemExecute : ILCARSCommand
    {
        public string Command { get; set; }

        public SystemExecute(string command)
        {
            Command = command;
        }

        public void OnRun()
        {
            Process.Start(Command);
        }
    }
}
