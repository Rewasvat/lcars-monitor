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
            Type? currentType = slot.AttachedChild?.GetType();

            Setup(slot.AttachedChild, typeof(LCARSControl));

            optionsBox.SelectionChanged += (object sender, SelectionChangedEventArgs e) =>
            {
                Type? selectedType = (Type?)optionsBox.SelectedValue;
                if (selectedType == null)
                {
                    slot.AttachedChild = null;
                }
                else if (!optionsBox.SelectedValue.Equals(currentType))
                {
                    slot.AttachedChild = Activator.CreateInstance(selectedType) as LCARSControl;
                }
                currentType = selectedType;
            };
        }

        public void SetAsCommandSelector()
        {
            // Setup(item.Command, typeof(ILCARSCommand));
        }

        public void Setup(object? obj, Type baseType)
        {
            var assembly = Assembly.GetAssembly(baseType)!;
            var types = assembly.GetTypes().Where(t => t != baseType && baseType.IsAssignableFrom(t));

            optionsBox.SelectedValuePath = "Type";
            optionsBox.DisplayMemberPath = "Name";

            optionsBox.Items.Add(new TypeSelectorEntry(null));
            foreach (var type in types)
            {
                optionsBox.Items.Add(new TypeSelectorEntry(type));
            }

            if (obj != null)
                optionsBox.SelectedValue = obj.GetType();
            else
                optionsBox.SelectedValue = null;
        }
    }

    internal class TypeSelectorEntry
    {
        public Type? Type { get; set; }
        public string Name
        {
            get
            {
                if (Type == null)
                    return "None";
                return Type.Name;
            }
        }

        public TypeSelectorEntry(Type? type) { Type = type; }
    }
}
