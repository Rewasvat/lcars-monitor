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
    /// Interaction logic for Board.xaml
    /// </summary>
    public partial class Board : LCARSControl, ILCARSMultiContainer
    {
        public Canvas ChildrenCanvas => canvas;
        public event ILCARSContainer.SlotsChangedEventHandler? SlotsChangedEvent;
        public Dictionary<string, Slot> Slots { get { return slots; } }

        private string[] boardNames = { "default" };
        [JsonProperty]
        public string[] BoardNames
        {
            get { return boardNames; }
            set
            {
                boardNames = value;
                UpdateSlots();
            }
        }

        private string currentBoard = "default";
        [JsonProperty]
        public string CurrentBoard
        {
            get { return currentBoard; }
            set
            {
                if (slots.ContainsKey(value))
                {
                    currentBoard = value;
                    UpdateCurrentBoard();
                }
            }
        }

        private Dictionary<string, Slot> slots;

        public Slot[] ChildSlots
        {
            get
            {
                return slots.Values.ToArray();
            }
        }

        public Slot CurrentSlot
        {
            get { return slots[CurrentBoard]; }
        }

        [JsonProperty]
        [IgnoreOnEditor]
        public DictControlEntry[] ChildControls
        {
            get
            {
                var children = new DictControlEntry[slots.Count];
                int index = 0;
                foreach (var item in slots)
                {
                    children[index] = new DictControlEntry
                    {
                        Key = item.Key,
                        Child = item.Value.AttachedChild
                    };
                    index++;
                }
                return children;
            }
            set
            {
                foreach (var item in value)
                {
                    slots[item.Key].AttachedChild = item.Child;
                }
            }
        }

        // METHODS

        public Board()
        {
            InitializeComponent();

            slots = new Dictionary<string, Slot>
            {
                ["default"] = new Slot(this, "default")
            };
            UpdateInternalArea();
        }

        protected void UpdateSlots()
        {
            List<string> toRemove = new List<string>();
            List<string> toAdd = new List<string>();

            // Remove old slots, add new ones as needed
            foreach (string name in BoardNames)
            {
                if (!slots.ContainsKey(name))
                    toAdd.Add(name);
            }
            foreach (string name in slots.Keys)
            {
                if (!boardNames.Contains(name))
                    toRemove.Add(name);
            }

            foreach (string name in toRemove)
            {
                slots[name].AttachedChild = null;
                slots.Remove(name);
            }
            foreach (string name in toAdd)
            {
                slots.Add(name, new Slot(this, name));
            }

            // Update slots area if required
            if (toAdd.Count > 0)
                UpdateInternalArea();

            // Update current board if required
            if (!slots.ContainsKey(currentBoard))
            {
                CurrentBoard = slots.Keys.First();
            }

            SlotsChangedEvent?.Invoke(this, new SlotsChangedEventArgs());
        }

        protected void UpdateCurrentBoard()
        {
            foreach (var item in slots)
            {
                item.Value.Enabled = item.Key == currentBoard;
            }
        }

        protected void UpdateInternalArea()
        {
            foreach (Slot slot in slots.Values)
            {
                var rect = slot.Area;
                rect.X = 0.0;
                rect.Y = 0.0;
                rect.Width = Math.Max(10, ActualWidth);
                rect.Height = Math.Max(10, ActualHeight);
                slot.Area = rect;
            }
        }

        private void OnSizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateInternalArea();
        }
    }

    public class DictControlEntry
    {
        public string Key { get; set; } = "";
        public LCARSControl? Child { get; set; }
    }
}
