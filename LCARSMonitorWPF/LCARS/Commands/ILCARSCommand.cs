using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LCARSMonitorWPF.LCARS.Commands
{
    public interface ILCARSCommand
    {
        public void OnRun();
    }
}
