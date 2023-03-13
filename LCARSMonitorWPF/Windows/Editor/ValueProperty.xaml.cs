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
using LCARSMonitor.LCARS;

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

            nameLabel.Content = prop.Name + ":";

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
            else if (prop.PropertyType.Equals(typeof(string[])))
            {
                SetAsStringArray((string[])value!);
                return;
            }
            else if (prop.PropertyType.Equals(typeof(string)))
            {
                var sensorFlag = prop.GetCustomAttribute<EditorSensorAttribute>();
                if (sensorFlag != null)
                    SetAsSensorID((string)value!, sensorFlag);
                else
                    SetAsPureString((string)value!);
                return;
            }

            Label badValueText = new Label();
            badValueText.Content = value;
            SetChildValueControl(badValueText);
        }

        private void SetChildValueControl(FrameworkElement element)
        {
            grid.Children.Add(element);
            element.SetValue(Grid.ColumnProperty, 1);
            element.HorizontalAlignment = HorizontalAlignment.Stretch;
            element.VerticalAlignment = VerticalAlignment.Center;
        }

        private void SetAsCombobox(IEnumerable<string> options, string? value)
        {
            ComboBox box = new ComboBox();
            SetChildValueControl(box);

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
            SetChildValueControl(box);

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
            SetChildValueControl(check);
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
            SetChildValueControl(box);

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
                // TODO: else aqui é um caso de erro. Mostrar no editor pro user ver
                // talvez deixar esse ValueProperty com um fundo vermelho ou algo assim? Talvez marcar os nodes na tree até esse Control vermelhos tb?
                // teria que tirar esse estado de erro ao passar pelo IF acima
                // pros nodes na tree (os controls) teria que verificar se pelo menos 1 property ta com erro (daria pra fazer via eventos?)
            };
        }

        private void SetAsPureString(string value)
        {
            TextBox box = new TextBox();
            box.Text = value;
            SetChildValueControl(box);

            box.TextChanged += (object sender, TextChangedEventArgs e) =>
            {
                if (Property != null)
                {
                    Property.SetValue(Object, box.Text);
                }
            };
        }

        private void SetAsSensorID(string value, EditorSensorAttribute sensorFlag)
        {
            ComboBox box = new ComboBox();
            SetChildValueControl(box);

            box.SelectedValuePath = "SensorID";
            box.DisplayMemberPath = "DisplayName";

            box.Items.Add(new EditorSensorEntry(null));
            foreach (var sensor in sensorFlag.Sensors)
            {
                var entry = new EditorSensorEntry(sensor);
                box.Items.Add(entry);
            }

            box.SelectedValue = value;

            box.SelectionChanged += (object sender, SelectionChangedEventArgs e) =>
            {
                if (Property != null)
                {
                    Property.SetValue(Object, box.SelectedValue);
                }
            };
        }

        private void SetAsStringArray(string[] values)
        {
            TextBox box = new TextBox();
            box.AcceptsReturn = true;
            box.TextWrapping = TextWrapping.Wrap;
            box.HorizontalScrollBarVisibility = ScrollBarVisibility.Disabled;
            box.VerticalScrollBarVisibility = ScrollBarVisibility.Auto;
            box.VerticalContentAlignment = VerticalAlignment.Stretch;
            SetChildValueControl(box);

            string sum = "";
            if (values.Length > 0)
                sum = values[0];
            for (int i = 1; i < values.Length; i++)
            {
                sum += $"\n{values[i]}";
            }
            box.Text = sum;

            box.TextChanged += (object sender, TextChangedEventArgs e) =>
            {
                if (Property != null)
                {
                    var lines = box.Text.Split("\n", StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
                    Property.SetValue(Object, lines);
                }
            };
        }
    }
}
