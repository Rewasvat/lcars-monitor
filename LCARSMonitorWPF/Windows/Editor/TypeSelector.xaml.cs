using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
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
using LCARSMonitorWPF.Controls;
using LCARSMonitorWPF.LCARS.Commands;
using LCARSMonitor.LCARS;

namespace LCARSMonitorWPF.Windows.Editor
{
    /// <summary>
    /// Interaction logic for TypeSelector.xaml
    /// </summary>
    public partial class TypeSelector : UserControl
    {
        public TypeSelector()
        {
            InitializeComponent();
        }

        public void SetAsControlSelector(Slot slot)
        {
            var items = GetOptionsForType(typeof(LCARSControl));
            foreach (var controlID in LCARSSystem.Global.GetSavedControlNames())
            {
                items.Add(new SavedControlEntry(controlID));
            }
            Setup(slot.AttachedChild, items);

            Type? currentType = slot.AttachedChild?.GetType();
            optionsBox.SelectionChanged += (object sender, SelectionChangedEventArgs e) =>
            {
                if (optionsBox.SelectedValue == null)
                {
                    slot.AttachedChild = null;
                }
                else if (optionsBox.SelectedValue is Type selectedType)
                {
                    if (!selectedType.Equals(currentType))
                    {
                        slot.AttachedChild = Activator.CreateInstance(selectedType) as LCARSControl;
                        currentType = selectedType;
                    }
                }
                else if (optionsBox.SelectedValue is string controlID)
                {
                    slot.AttachedChild = LCARSSystem.Global.LoadControl(controlID);
                }
            };
        }

        public void SetAsCommandSelector(CommandSlot slot)
        {
            Setup(slot.Command, GetOptionsForType(typeof(ILCARSCommand)));

            Type? currentType = slot.Command?.GetType();
            optionsBox.SelectionChanged += (object sender, SelectionChangedEventArgs e) =>
            {
                Type? selectedType = (Type?)optionsBox.SelectedValue;
                if (selectedType == null)
                {
                    slot.Command = null;
                }
                else if (!optionsBox.SelectedValue.Equals(currentType))
                {
                    slot.Command = Activator.CreateInstance(selectedType) as ILCARSCommand;
                }
                currentType = selectedType;
            };
        }

        private List<ISelectorEntry> GetOptionsForType(Type baseType)
        {
            var assembly = Assembly.GetAssembly(baseType)!;
            var types = assembly.GetTypes().Where(t => t != baseType && baseType.IsAssignableFrom(t));

            List<ISelectorEntry> items = new List<ISelectorEntry>();
            items.Add(new TypeSelectorEntry(null));
            foreach (var type in types)
            {
                items.Add(new TypeSelectorEntry(type));
            }
            return items;
        }

        private void Setup(object? obj, List<ISelectorEntry> items)
        {
            optionsBox.SelectedValuePath = "Value";
            optionsBox.DisplayMemberPath = "Name";

            foreach (var item in items)
            {
                optionsBox.Items.Add(item);
            }

            if (obj != null)
                optionsBox.SelectedValue = obj.GetType();
            else
                optionsBox.SelectedValue = null;
        }
    }

    public interface ISelectorEntry
    {
        public string Name { get; }
        public object? Value { get; set; }
    }

    public class TypeSelectorEntry : ISelectorEntry
    {
        public object? Value { get; set; }
        public string Name
        {
            get
            {
                if (Value is Type type)
                    return $"NEW: {type.Name}";
                return "None";
            }
        }

        public TypeSelectorEntry(Type? type) { Value = type; }
    }

    public class SavedControlEntry : ISelectorEntry
    {
        public object? Value { get; set; }
        public string Name
        {
            get
            {
                return $"SAVED: {Value}";
            }
        }

        public SavedControlEntry(string id) { Value = id; }
    }
}
