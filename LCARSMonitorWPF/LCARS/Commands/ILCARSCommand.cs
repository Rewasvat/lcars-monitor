using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LCARSMonitorWPF.LCARS.Commands
{
    public interface ILCARSCommand
    {
        public CommandSlot? ParentSlot { get; internal set; }
        public void OnRun();
    }

    public class CommandSlot
    {
        public string Name { get; }
        public ILCARSCommandContainer Parent { get; }

        private ILCARSCommand? command;
        public ILCARSCommand? Command
        {
            get { return command; }
            set
            {
                if (command != null)
                    command.ParentSlot = null;

                command = value;

                if (command != null)
                    command.ParentSlot = this;

                RaiseCommandChanged();
            }
        }

        public delegate void CommandChangedEventHandler(object sender, CommandChangedEventArgs x);
        public event CommandChangedEventHandler? CommandChangedEvent;

        public CommandSlot(string name, ILCARSCommandContainer parent)
        {
            Name = name;
            Parent = parent;
        }

        protected virtual void RaiseCommandChanged()
        {
            CommandChangedEvent?.Invoke(this, new CommandChangedEventArgs());
        }
    }

    public class CommandChangedEventArgs { }

    public interface ILCARSCommandContainer
    {
        public Dictionary<string, CommandSlot> Commands { get; }
    }
}
