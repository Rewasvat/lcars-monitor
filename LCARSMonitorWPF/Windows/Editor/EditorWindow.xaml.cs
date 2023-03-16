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
using System.Windows.Shapes;
using LCARSMonitor.LCARS;
using LCARSMonitorWPF.Controls;
using LCARSMonitorWPF.LCARS.Commands;
using Newtonsoft.Json;
using Button = LCARSMonitorWPF.Controls.Button;

namespace LCARSMonitorWPF.Windows.Editor
{
    /// <summary>
    /// Interaction logic for EditorWindow.xaml
    /// </summary>
    public partial class EditorWindow : Window
    {
        private ControlTreeItem? rootItem;

        public EditorWindow()
        {
            InitializeComponent();

            ResetFullTree();
        }

        public void ResetFullTree()
        {
            rootItem?.Dispose();
            tree.Items.Clear();

            if (LCARSSystem.Global.RootSlot != null)
            {
                rootItem = new ControlTreeItem();
                rootItem.PropertiesList = propertiesList;
                rootItem.Slot = LCARSSystem.Global.RootSlot;

                tree.Items.Add(rootItem);
            }
        }
    }

    public class ControlTreeItem : TreeViewItem
    {
        private Slot? slot;
        public Slot? Slot
        {
            get { return slot; }
            set
            {
                UpdateSlot(value);
            }
        }
        public LCARSControl? Control
        {
            get { return Slot?.AttachedChild; }
        }

        public ListBox? PropertiesList { get; set; }

        // METHODS
        public ControlTreeItem()
        {
            MouseDoubleClick += OnDoubleClick;
        }

        protected void UpdateSlot(Slot? newSlot)
        {
            Dispose();

            slot = newSlot;

            if (slot != null)
                slot.ChildChangedEvent += OnControlChanged;

            UpdateControl();
        }

        protected void UpdateControl()
        {
            // TODO: include Slot Name/Identifier
            if (Control != null)
                Header = $"{Control.ID} ({Control.GetType().Name})";
            else
                Header = "EMPTY SLOT";

            if (Control is ILCARSContainer container)
            {
                container.SlotsChangedEvent += OnChildSlotsChanged;
            }
            PopulateChildren();
        }

        protected void PopulateChildren()
        {
            if (Control is ILCARSCommandContainer commandContainer)
            {
                foreach (var item in commandContainer.Commands)
                {
                    AddCommandSlot(item.Value);
                }
            }

            if (Control is ILCARSContainer container)
            {
                foreach (var childSlot in container.GetChildSlots())
                {
                    AddChildSlot(childSlot);
                }
            }
        }

        protected void AddChildSlot(Slot childSlot)
        {
            ControlTreeItem childItem = new ControlTreeItem();
            childItem.PropertiesList = PropertiesList;
            childItem.Slot = childSlot;
            Items.Add(childItem);
        }

        protected void AddCommandSlot(CommandSlot commandSlot)
        {
            CommandTreeItem commandItem = new CommandTreeItem();
            commandItem.PropertiesList = PropertiesList;
            commandItem.Slot = commandSlot;
            Items.Add(commandItem);
        }

        protected void ClearChildren()
        {
            foreach (var item in Items)
            {
                if (item is ControlTreeItem controlItem)
                {
                    controlItem.Dispose();
                }
                else if (item is CommandTreeItem commandItem)
                {
                    commandItem.Dispose();
                }
            }
            Items.Clear();
        }

        public void Dispose()
        {
            // Remove event handlers and children
            if (slot != null)
                slot.ChildChangedEvent += OnControlChanged;
            if (Control is ILCARSContainer container)
                container.SlotsChangedEvent -= OnChildSlotsChanged;
            ClearChildren();
        }

        protected void UpdatePropertiesList()
        {
            if (!IsSelected || PropertiesList == null || Slot == null)
                return;

            PropertiesList.Items.Clear();

            var typeSelector = new TypeSelector();
            typeSelector.SetAsControlSelector(Slot);
            PropertiesList.Items.Add(typeSelector);

            if (Control == null)
            {
                return;
            }

            var props = Control.GetType().GetProperties().Where(
                prop => Attribute.IsDefined(prop, typeof(JsonPropertyAttribute)) && !Attribute.IsDefined(prop, typeof(IgnoreOnEditorAttribute))
            );
            foreach (var prop in props)
            {
                ValueProperty handler = new ValueProperty();
                handler.BuildFor(prop, Control);
                PropertiesList.Items.Add(handler);
            }
        }

        protected void OnControlChanged(object sender, ChildChangedEventArgs e)
        {
            // When our control changes (that is, the AttachedChild of our slot)
            // We basically need to reset our content: erase all children and update content (including adding possible children)
            ClearChildren();
            UpdateControl();
            UpdatePropertiesList();
        }

        protected void OnChildSlotsChanged(object sender, SlotsChangedEventArgs e)
        {
            // When our Child Slots changes (that is, the ChildSlots of our control have changed)
            // Then we only need to update our children content: so erase all children and re-populate them.
            ClearChildren();
            PopulateChildren();
        }

        private void OnDoubleClick(object sender, MouseButtonEventArgs e)
        {
            UpdatePropertiesList();
        }
    }

    public class CommandTreeItem : TreeViewItem
    {
        public ListBox? PropertiesList { get; set; }

        private CommandSlot? slot;
        public CommandSlot? Slot
        {
            get { return slot; }
            set
            {
                UpdateSlot(value);
            }
        }
        public ILCARSCommand? Command { get { return slot?.Command; } }

        public CommandTreeItem()
        {
            MouseDoubleClick += OnDoubleClick;
        }

        protected void UpdateSlot(CommandSlot? newSlot)
        {
            Dispose();

            slot = newSlot;

            if (slot != null)
                slot.CommandChangedEvent += OnCommandChanged;

            UpdateCommand();
        }

        protected void UpdateCommand()
        {
            if (Command != null)
                Header = $"{slot!.Name}: {Command.GetType().Name}";
            else
                Header = $"{slot!.Name}: NO COMMAND";
        }

        protected void UpdatePropertiesList()
        {
            if (!IsSelected || PropertiesList == null || Slot == null)
                return;

            PropertiesList.Items.Clear();

            var typeSelector = new TypeSelector();
            typeSelector.SetAsCommandSelector(Slot);
            PropertiesList.Items.Add(typeSelector);

            if (Command == null)
            {
                return;
            }

            var props = Command.GetType().GetProperties();
            foreach (var prop in props)
            {
                ValueProperty handler = new ValueProperty();
                handler.BuildFor(prop, Command);
                PropertiesList.Items.Add(handler);
            }
        }

        public void Dispose()
        {
            if (slot != null)
                slot.CommandChangedEvent += OnCommandChanged;
        }

        private void OnCommandChanged(object sender, CommandChangedEventArgs e)
        {
            UpdateCommand();
            UpdatePropertiesList();
        }

        private void OnDoubleClick(object sender, MouseButtonEventArgs e)
        {
            UpdatePropertiesList();
        }
    }
}
