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
using Newtonsoft.Json;

namespace LCARSMonitorWPF.Controls
{
    /// <summary>
    /// Interaction logic for AxisList.xaml
    /// </summary>
    public partial class AxisList : LCARSControl, ILCARSMultiContainer
    {
        public Canvas ChildrenCanvas => canvas;
        public event ILCARSContainer.SlotsChangedEventHandler? SlotsChangedEvent;

        private AxisOrientation orientation = AxisOrientation.Horizontal;
        [JsonProperty]
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
        [JsonProperty]
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

        private double padding = 0.0;
        [JsonProperty]
        public double ChildrenPadding
        {
            get { return padding; }
            set
            {
                padding = value;
                UpdateChildren();
            }
        }

        private Slot[] slots;
        public Slot[] ChildSlots { get { return slots; } }

        [JsonProperty]
        [IgnoreOnEditor]
        public LCARSControl?[] ChildControls
        {
            get
            {
                LCARSControl?[] children = new LCARSControl?[ChildSlots.Length];
                for (int i = 0; i < ChildSlots.Length; i++)
                    children[i] = ChildSlots[i].AttachedChild;
                return children;
            }
            set
            {
                for (int i = 0; i < value.Length; i++)
                {
                    ChildSlots[i].AttachedChild = value[i];
                }
            }
        }

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

                SlotsChangedEvent?.Invoke(this, new SlotsChangedEventArgs());
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
            axisSize -= padding * (slotPieces.Length + 1);
            double pieceSize = axisSize / totalSlotPieces;
            double position = padding;
            for (int i = 0; i < slots.Length; i++)
            {
                Slot slot = slots[i];
                double numPieces = slotPieces[i];
                double size = pieceSize * numPieces;

                var rect = slot.Area;
                if (Orientation == AxisOrientation.Horizontal)
                {
                    rect.X = position;
                    rect.Y = padding;
                    rect.Width = Math.Max(10, size);
                    rect.Height = Math.Max(10, ActualHeight - padding);
                }
                else
                {
                    rect.X = padding;
                    rect.Y = position;
                    rect.Width = Math.Max(10, ActualWidth - padding);
                    rect.Height = Math.Max(10, size);
                }
                slot.Area = rect;

                position += size + padding;
            }
        }

        private void LCARSControl_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateChildren();
        }

    }
}
