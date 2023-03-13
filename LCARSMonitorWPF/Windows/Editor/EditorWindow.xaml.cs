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

        public void AddCommandToTree(Button control, ItemCollection parentItems)
        {
            CommandTreeItem item = new CommandTreeItem();
            if (control.OnClick != null)
                item.Header = $"{control.OnClick.GetType().ToString()}";
            else
                item.Header = "NO COMMAND";
            parentItems.Add(item);
            item.Command = control.OnClick;
            item.ParentControl = control;
            item.MouseDoubleClick += OnCommandItemDoubleClick;
        }

        private void OnCommandItemDoubleClick(object sender, MouseButtonEventArgs e)
        {
            CommandTreeItem? item = e.Source as CommandTreeItem;
            if (item == null || !item.IsSelected)
                return;

            propertiesList.Items.Clear();

            var typeSelector = new TypeSelector();
            typeSelector.SetAsCommandSelector();
            propertiesList.Items.Add(typeSelector);

            if (item.Command == null)
            {
                return;
            }

            var props = item.Command.GetType().GetProperties();
            foreach (var prop in props)
            {
                ValueProperty handler = new ValueProperty();
                handler.BuildFor(prop, item.Command);
                propertiesList.Items.Add(handler);
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
            if (Control != null)
                Header = $"{Control.ID} ({Control.GetType().Name})";
            else
                Header = "EMPTY SLOT";

            if (Control is ILCARSContainer container)
            {
                container.SlotsChangedEvent += OnChildSlotsChanged;
                PopulateChildren(container);
            }
        }

        protected void PopulateChildren(ILCARSContainer container)
        {
            // if (Control is Button button)
            // {
            //     // TODO: fix this to properly get the commands the control may have or not
            //     AddCommandToTree(button, Items);
            // }

            foreach (var childSlot in container.GetChildSlots())
            {
                AddChildSlot(childSlot);
            }
        }

        protected void AddChildSlot(Slot childSlot)
        {
            ControlTreeItem childItem = new ControlTreeItem();
            childItem.PropertiesList = PropertiesList;
            childItem.Slot = childSlot;
            Items.Add(childItem);
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
                    // TODO: clear CommandItem
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
            if (Control is ILCARSContainer container)
            {
                PopulateChildren(container);
            }
        }

        private void OnDoubleClick(object sender, MouseButtonEventArgs e)
        {
            UpdatePropertiesList();
        }
    }

    public class CommandTreeItem : TreeViewItem
    {
        public Button? ParentControl { get; set; }
        public ILCARSCommand? Command { get; set; }
    }
}
