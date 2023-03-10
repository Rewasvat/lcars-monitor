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
    /// Interaction logic for Board.xaml
    /// </summary>
    public partial class Board : LCARSControl, ILCARSMultiContainer
    {
        private Dictionary<string, Slot> slots;
        public Slot[] ChildSlots
        {
            get
            {
                return slots.Values.ToArray();
            }
        }
        public Canvas ChildrenCanvas => canvas;

        public Dictionary<string, Slot> Slots { get { return slots; } }

        private string[] boardNames = { "default" };
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

        public Slot CurrentSlot
        {
            get { return slots[CurrentBoard]; }
        }

        // METHODS

        public Board()
        {
            InitializeComponent();

            slots = new Dictionary<string, Slot>
            {
                ["default"] = new Slot(this)
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
                slots.Add(name, new Slot(this));
            }

            // Update slots area if required
            if (toAdd.Count > 0)
                UpdateInternalArea();

            // Update current board if required
            if (!slots.ContainsKey(currentBoard))
            {
                CurrentBoard = slots.Keys.First();
            }
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

        ////  SERIALIZATION

        protected override LCARSControlData CreateDataObject()
        {
            Dictionary<string, LCARSControlData?> children = new Dictionary<string, LCARSControlData?>(slots.Count);
            foreach (var item in slots)
            {
                children[item.Key] = item.Value.AttachedChild?.Serialize();
            }

            return new BoardData
            {
                BoardNames = BoardNames,
                CurrentBoard = CurrentBoard,
                Children = children,
            };
        }

        protected override void LoadDataInternal(LCARSControlData baseData)
        {
            var data = baseData as BoardData;
            if (data == null)
                return;
            BoardNames = data.BoardNames!;
            CurrentBoard = data.CurrentBoard!;

            if (data.Children != null)
            {
                foreach (var item in data.Children)
                {
                    slots[item.Key].AttachedChild = Deserialize(item.Value);
                }
            }
        }
    }

    public class BoardData : LCARSControlData
    {
        public string[]? BoardNames { get; set; }
        public string? CurrentBoard { get; set; }
        public Dictionary<string, LCARSControlData?>? Children { get; set; }
    }
}
