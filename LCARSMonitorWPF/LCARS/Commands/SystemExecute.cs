using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using Newtonsoft.Json;

namespace LCARSMonitorWPF.LCARS.Commands
{
    [JsonObject(MemberSerialization.OptIn)]
    public class SystemExecute : ILCARSCommand
    {
        public CommandSlot? ParentSlot { get; set; }

        [JsonProperty]
        public string Command { get; set; } = "";

        public void OnRun()
        {
            if (Command.Length > 0)
                Process.Start(Command);
        }
    }
}
