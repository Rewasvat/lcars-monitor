using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using LCARSMonitorWPF.Controls;
using Newtonsoft.Json;

namespace LCARSMonitorWPF.LCARS.Commands
{
    [JsonObject(MemberSerialization.OptIn)]
    public class ChangeBoard : ILCARSCommand
    {
        public CommandSlot? ParentSlot { get; set; }

        [JsonProperty]
        public string TargetBoard { get; set; } = "";
        [JsonProperty]
        public string BoardToSelect { get; set; } = "";

        public void OnRun()
        {
            if (TargetBoard.Length <= 0 || BoardToSelect.Length <= 0)
                return;

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
