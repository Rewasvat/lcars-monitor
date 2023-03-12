using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
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

namespace LCARSMonitorWPF.Windows.Editor
{
    /// <summary>
    /// Interaction logic for ValueProperty.xaml
    /// </summary>
    public partial class ValueProperty : UserControl
    {
        public PropertyInfo? Property { get; protected set; }
        public object? Object { get; protected set; }

        // METHODS

        public ValueProperty()
        {
            InitializeComponent();
        }

        public void BuildFor(PropertyInfo prop, object obj)
        {
            Property = prop;
            Object = obj;

            nameLabel.Content = prop.Name;
            /*
            - string []
            - string (ID):
                - verificar com o System se pode deixar tal ID, ai previne ter duplicatas
            - string (com lista de opcoes, quase como uma enum) <usaria com lista de sensor IDs pra selecionar>
            */
            var value = prop.GetValue(obj);

            if (prop.PropertyType.IsEnum)
            {
                var flags = prop.PropertyType.GetCustomAttribute<FlagsAttribute>();
                var values = new List<string>();
                foreach (object val in Enum.GetValues(prop.PropertyType))
                {
                    values.Add(val.ToString()!);
                }
                if (flags != null)
                {
                    SetAsFlags(values, value?.ToString());
                }
                else
                {
                    SetAsCombobox(values, value?.ToString());
                }
                return;
            }
            else if (prop.PropertyType.Equals(typeof(bool)))
            {
                SetAsBoolean((bool)value!);
                return;
            }
            else if (prop.PropertyType.Equals(typeof(double)))
            {
                SetAsDouble((double)value!);
                return;
            }
            else if (prop.PropertyType.Equals(typeof(string)))
            {
                SetAsPureString((string)value!);
                return;
            }

            Label badValueText = new Label();
            badValueText.Content = value;
            valueHolder.Child = badValueText;
        }

        private void SetAsCombobox(IEnumerable<string> options, string? value)
        {
            ComboBox box = new ComboBox();
            valueHolder.Child = box;

            foreach (var option in options)
                box.Items.Add(option);

            box.SelectedItem = value;

            box.SelectionChanged += (object sender, SelectionChangedEventArgs e) =>
            {
                if (Property != null)
                {
                    if (Property.PropertyType.IsEnum)
                        Property.SetValue(Object, Enum.Parse(Property.PropertyType, (string)box.SelectedItem!));
                    else
                        Property.SetValue(Object, box.SelectedItem);
                }
            };
        }

        private void SetAsFlags(IEnumerable<string> options, string? value)
        {
            ListBox box = new ListBox();
            valueHolder.Child = box;

            RoutedEventHandler onChecked = (object sender, RoutedEventArgs e) =>
            {
                if (Property != null)
                {
                    string sumFlags = "";
                    foreach (var item in box.Items.Cast<CheckBox>())
                    {
                        if (item != null)
                            if ((bool)item.IsChecked!)
                                sumFlags += $"{item.Content}, ";
                    }

                    if (sumFlags.Length > 0)
                        sumFlags = sumFlags.Remove(sumFlags.Length - 2);

                    Property.SetValue(Object, Enum.Parse(Property.PropertyType, sumFlags));
                }
            };

            foreach (var option in options)
            {
                CheckBox check = new CheckBox();
                check.IsChecked = value?.Contains(option);
                check.Content = option;
                box.Items.Add(check);
                check.Checked += onChecked;
                check.Unchecked += onChecked;
            }
        }

        private void SetAsBoolean(bool value)
        {
            CheckBox check = new CheckBox();
            valueHolder.Child = check;
            check.IsChecked = value;

            RoutedEventHandler onChecked = (object sender, RoutedEventArgs e) =>
            {
                if (Property != null)
                {
                    Property.SetValue(Object, check.IsChecked);
                }
            };
            check.Checked += onChecked;
            check.Unchecked += onChecked;
        }

        private void SetAsDouble(double value)
        {
            TextBox box = new TextBox();
            box.Text = value.ToString();
            valueHolder.Child = box;

            box.PreviewTextInput += (object sender, TextCompositionEventArgs e) =>
            {
                Regex regex = new Regex(@"^[-+]?[0-9]*\.?[0-9]+$");
                e.Handled = !regex.IsMatch(e.Text);
            };

            box.TextChanged += (object sender, TextChangedEventArgs e) =>
            {
                double newValue;
                if (double.TryParse(box.Text, out newValue) && Property != null)
                {
                    Property.SetValue(Object, newValue);
                }
            };
        }

        private void SetAsPureString(string value)
        {
            TextBox box = new TextBox();
            box.Text = value;
            valueHolder.Child = box;

            box.TextChanged += (object sender, TextChangedEventArgs e) =>
            {
                if (Property != null)
                {
                    Property.SetValue(Object, box.Text);
                }
            };
        }
    }
}
