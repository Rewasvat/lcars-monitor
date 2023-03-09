using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using LCARSMonitorWPF.Controls;

namespace LCARSMonitorWPF.LCARS.Commands
{
    public class ChangeBoard : ILCARSCommand
    {
        public string TargetBoard { get; set; }
        public string BoardToSelect { get; set; }

        public ChangeBoard(string targetBoard, string boardToSelect)
        {
            TargetBoard = targetBoard;
            BoardToSelect = boardToSelect;
        }

        public void OnRun()
        {
            Board target = new Board(); // TODO: FIX THIS get Board with TargetBoard name
            target.CurrentBoard = BoardToSelect;
        }
    }
}
