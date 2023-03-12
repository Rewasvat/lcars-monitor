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
        public EditorWindow()
        {
            InitializeComponent();

            LCARSMonitorWPF.Controls.Board? board = LCARSMonitor.LCARS.LCARSSystem.Global.GetControlByName("RootBoard") as LCARSMonitorWPF.Controls.Board;
            if (board != null)
            {
                AddControlToTree(board, null, tree.Items);
            }
        }

        public void AddControlToTree(LCARSControl? control, Slot? parentSlot, ItemCollection parentItems)
        {
            ControlTreeItem item = new ControlTreeItem();
            if (control != null)
                item.Header = $"{control.ID} ({control.GetType().Name})";
            else
                item.Header = "EMPTY SLOT";
            parentItems.Add(item);
            item.Control = control;
            item.Slot = parentSlot;
            item.MouseDoubleClick += OnControlItemDoubleClick;

            if (control is Button button)
            {
                // TODO: fix this to properly get the commands the control may have or not
                AddCommandToTree(button, item.Items);
            }

            if (control is ILCARSContainer container)
            {
                foreach (var slot in container.GetChildSlots())
                {
                    AddControlToTree(slot.AttachedChild, slot, item.Items);
                }
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

        private void OnControlItemDoubleClick(object sender, MouseButtonEventArgs e)
        {
            ControlTreeItem? item = e.Source as ControlTreeItem;
            if (item == null || !item.IsSelected)
                return;

            propertiesList.Items.Clear();
            // TODO: inserir "property" pra selecionar tipo do control (opcoes: lista de LCARSControl types + NONE)
            //  - assim user pode selecionar o tipo do control em um slot, incluindo trocar de tipo e remover control (selectionando tipo NONE)
            if (item.Control == null)
            {
                return;
            }

            var props = item.Control.GetType().GetProperties().Where(
                prop => Attribute.IsDefined(prop, typeof(JsonPropertyAttribute)) && !Attribute.IsDefined(prop, typeof(IgnoreOnEditorAttribute))
            );
            foreach (var prop in props)
            {
                ValueProperty handler = new ValueProperty();
                handler.BuildFor(prop, item.Control);
                propertiesList.Items.Add(handler);
            }
        }

        private void OnCommandItemDoubleClick(object sender, MouseButtonEventArgs e)
        {
            CommandTreeItem? item = e.Source as CommandTreeItem;
            if (item == null || !item.IsSelected)
                return;

            propertiesList.Items.Clear();
            // TODO: inserir "property" pra selecionar tipo do comando (opcoes: lista de ILCARSCommand types + NONE)
            //  - assim user pode selecionar o tipo do comando, incluindo trocar de tipo e remover comando (selectionando tipo NONE)
            if (item.Command == null)
            {
                return;
            }

            var props = item.Command.GetType().GetProperties();
            int index = 0;
            foreach (var prop in props)
            {
                Label label = new Label();
                label.Content = $"[{prop.PropertyType}] {prop.Name}: {prop.GetValue(item.Command)}";
                label.SetValue(Grid.RowProperty, index);
                index++;

                propertiesList.Items.Add(label);
            }
        }
    }

    public class ControlTreeItem : TreeViewItem
    {
        public Slot? Slot { get; set; }
        public LCARSControl? Control { get; set; }
    }
    public class CommandTreeItem : TreeViewItem
    {
        public Button? ParentControl { get; set; }
        public ILCARSCommand? Command { get; set; }
    }
}
