using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using Newtonsoft.Json;

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
                    UpdateChildVisibility();
                    RaiseChildChanged();
                }
            }
        }

        public string Name { get; }

        private Rect area;
        public Rect Area
        {
            get { return area; }
            set
            {
                area = value;
                child?.OnAttachToSlot(this);
                UpdateChildVisibility();
            }
        }

        private bool enabled = true;
        public bool Enabled
        {
            get { return enabled; }
            set
            {
                enabled = value;
                UpdateChildVisibility();
            }
        }

        public delegate void ChildChangedEventHandler(object sender, ChildChangedEventArgs x);
        public event ChildChangedEventHandler? ChildChangedEvent;

        public Slot(ILCARSContainer parent, string name)
        {
            this.parent = parent;
            Name = name;
        }

        protected void UpdateChildVisibility()
        {
            if (AttachedChild != null)
            {
                if (enabled)
                {
                    AttachedChild.IsEnabled = true;
                    AttachedChild.Visibility = System.Windows.Visibility.Visible;
                }
                else
                {
                    AttachedChild.IsEnabled = false;
                    AttachedChild.Visibility = System.Windows.Visibility.Hidden;
                }
            }
        }

        protected virtual void RaiseChildChanged()
        {
            ChildChangedEvent?.Invoke(this, new ChildChangedEventArgs());
        }
    }

    public interface ILCARSContainer
    {
        public Canvas ChildrenCanvas { get; }
        internal void UpdateChildSlot(Slot slot, LCARSControl? newChild)
        {
            // NOTE: not checking if slot belongs to this container for simplicity, but maybe we should

            if (slot.AttachedChild != null)
                ChildrenCanvas.Children.Remove(slot.AttachedChild);  // removing previous child
            if (newChild != null)
                ChildrenCanvas.Children.Add(newChild);
        }

        public List<Slot> GetChildSlots()
        {
            var slots = new List<Slot>();
            if (this is ILCARSSingleContainer single)
            {
                slots.Add(single.ChildSlot);
            }
            else if (this is ILCARSMultiContainer multi)
            {
                slots.AddRange(multi.ChildSlots);
            }
            return slots;
        }

        public delegate void SlotsChangedEventHandler(object sender, SlotsChangedEventArgs x);
        public event SlotsChangedEventHandler? SlotsChangedEvent;
    }
    public interface ILCARSSingleContainer : ILCARSContainer
    {
        public Slot ChildSlot { get; }
    }
    public interface ILCARSMultiContainer : ILCARSContainer
    {
        public Slot[] ChildSlots { get; }
    }

    public class SlotsChangedEventArgs { }
    public class ChildChangedEventArgs { }
}
