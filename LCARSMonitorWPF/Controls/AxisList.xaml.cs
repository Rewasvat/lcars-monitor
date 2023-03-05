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

namespace LCARSMonitorWPF.Controls
{
    /// <summary>
    /// Interaction logic for AxisList.xaml
    /// </summary>
    public partial class AxisList : LCARSControl, ILCARSMultiContainer
    {
        private Slot[] slots;
        public Slot[] ChildSlots { get { return slots; } }

        private AxisOrientation orientation = AxisOrientation.Horizontal;
        public AxisOrientation Orientation
        {
            get { return orientation; }
            set
            {
                if (orientation != value)
                {
                    orientation = value;
                    UpdateChildren();
                }
            }
        }

        private string config = "1";
        public string Config
        {
            get { return config; }
            set
            {
                if (config != value)
                {
                    config = value;
                    UpdateChildren();
                }
            }
        }

        // TODO: implementar padding entre elementos

        // METHODS
        public AxisList()
        {
            InitializeComponent();

            slots = new Slot[] {
                new Slot(this)
            };

            UpdateChildren();
        }

        public void UpdateChildren()
        {
            string[] slotConfigs = Config.Split("/", StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);

            if (slotConfigs.Length != slots.Length)
            {
                // Number of slots mismatch - gotta update our slot array

                for (int i = slotConfigs.Length; i < slots.Length; i++)
                {
                    // remove old slots
                    // This is done before altering or 'slots' attribute so that common slot logic works
                    // it will call updateChildSlot and remove the child from us, and update the now orphaned child.
                    slots[i].AttachedChild = null;
                }

                Slot[] oldSlots = (Slot[])slots.Clone();
                slots = new Slot[slotConfigs.Length];
                for (int i = 0; i < slotConfigs.Length; i++)
                {
                    if (i < oldSlots.Length)
                    {
                        // reuse previous slot
                        slots[i] = oldSlots[i];
                    }
                    else
                    {
                        // create new slot
                        slots[i] = new Slot(this);
                    }
                }
            }

            // Convert config to numerical values and calculate total sum
            double[] slotPieces = new double[slotConfigs.Length];
            double totalSlotPieces = 0.0;
            for (int i = 0; i < slotPieces.Length; i++)
            {
                slotPieces[i] = Double.Parse(slotConfigs[i]);
                totalSlotPieces += slotPieces[i];
            }

            double axisSize = Orientation == AxisOrientation.Horizontal ? ActualWidth : ActualHeight;
            double pieceSize = axisSize / totalSlotPieces;
            double position = 0.0;
            for (int i = 0; i < slots.Length; i++)
            {
                Slot slot = slots[i];
                double numPieces = slotPieces[i];
                double size = pieceSize * numPieces;

                var rect = slot.Area;
                if (Orientation == AxisOrientation.Horizontal)
                {
                    rect.X = position;
                    rect.Y = 0.0;
                    rect.Width = Math.Max(10, size);
                    rect.Height = Math.Max(10, ActualHeight);
                }
                else
                {
                    rect.X = 0.0;
                    rect.Y = position;
                    rect.Width = Math.Max(10, ActualWidth);
                    rect.Height = Math.Max(10, size);
                }
                slot.Area = rect;

                position += size;
            }
        }

        public void UpdateChildSlot(Slot slot, LCARSControl? newChild)
        {
            if (!slots.Contains(slot))
            {
                // throw error?
                throw new ArgumentException("Tried to update a slot that is not our child slot", "slot");
            }

            if (slot.AttachedChild != null)
                canvas.Children.Remove(slot.AttachedChild);  // removing previous child
            if (newChild != null)
                canvas.Children.Add(newChild);
        }

        private void LCARSControl_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateChildren();
        }
    }
}
