using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace LCARSMonitorWPF.Controls
{
    public class Slot
    {
        private ILCARSContainer parent;
        public LCARSControl? Parent
        {
            get { return parent as LCARSControl; }
        }

        private LCARSControl? child;
        public LCARSControl? AttachedChild
        {
            get { return child; }
            set
            {
                if (value != child)
                {
                    parent.UpdateChildSlot(this, value);
                    child?.OnAttachToSlot(null);
                    child = value;
                    child?.OnAttachToSlot(this);
                }
            }
        }

        private Rect area;
        public Rect Area
        {
            get { return area; }
            set
            {
                area = value;
                child?.OnAttachToSlot(this);
            }
        }

        public Slot(ILCARSContainer parent)
        {
            this.parent = parent;
        }
    }

    public interface ILCARSContainer
    {
        public void UpdateChildSlot(Slot slot, LCARSControl? newChild);
    }
    public interface ILCARSSingleContainer : ILCARSContainer
    {
        public Slot ChildSlot { get; }
    }
    public interface ILCARSMultiContainer : ILCARSContainer
    {
        public Slot[] ChildSlots { get; }
    }
}
