using System;
using System.Collections.Generic;
using System.Diagnostics;
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
            Board? target = LCARSMonitor.LCARS.LCARSSystem.Global.GetControlByName(TargetBoard) as Board;
            if (target != null)
            {
                target.CurrentBoard = BoardToSelect;
                Debug.WriteLine($"{TargetBoard}: changed selected board to '{BoardToSelect}'");
            }
            else
            {
                Debug.WriteLine($"Couldn't find target Board '{TargetBoard}'");
            }
        }
    }
}
