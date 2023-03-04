using System;
using System.Collections.Generic;
using System.Diagnostics;
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
    /// Interaction logic for Button.xaml
    /// </summary>
    public partial class Button : LCARSControl
    {
        // PROPERTIES
        public Stumps Stumps
        {
            get { return (Stumps)GetValue(StumpsProperty); }
            set { SetValue(StumpsProperty, value); }
        }
        public static readonly DependencyProperty StumpsProperty = DependencyProperty.Register(
            "Stumps",
            typeof(Stumps),
            typeof(Button),
            new PropertyMetadata(Stumps.Both, StumpsChanged)
        );
        private static void StumpsChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            (d as Button)?.UpdateCorners();
        }

        private Slot slot;
        public Slot Slot
        {
            get { return slot; }
            set
            {
                slot = value;
                // TODO: vai ter que atualizar tamanho/visual/corner e tal
            }
        }

        public Visuals VisualStyle
        {
            get { return (Visuals)GetValue(VisualStyleProperty); }
            set { SetValue(VisualStyleProperty, value); }
        }
        public static readonly DependencyProperty VisualStyleProperty = DependencyProperty.Register(
            "VisualStyle",
            typeof(Visuals),
            typeof(Button),
            new PropertyMetadata(Visuals.Common, StyleChanged)
        );
        private static void StyleChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is Button obj)
            {
                obj.Visual = Visual.GetVisual(obj.VisualStyle);
            }
        }

        private Visual lcarsVisual = Visual.Common;
        public Visual Visual
        {
            get { return lcarsVisual; }
            set
            {
                lcarsVisual = value;
                UpdateVisual();
            }
        }

        public string Label
        {
            get { return (string)GetValue(LabelProperty); }
            set { SetValue(LabelProperty, value); }
            // TODO: suportar mudar tamanho do texto?
            // TODO: poder mudar alinhamento do texto?
            // TODO: suportar mudar cor do texto dinamicamente baseado em outros fatores
            //      - incluir no Style, cor do texto em cada estado
        }
        public static readonly DependencyProperty LabelProperty = DependencyProperty.Register(
            "Label",
            typeof(string),
            typeof(Button),
            new PropertyMetadata(string.Empty, LabelChanged)
        );
        private static void LabelChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is Button obj)
            {
                obj.label.Content = obj.Label;
            }
        }


        // INTERNAL ATTRIBUTES
        protected SolidColorBrush FillBrush;
        private bool hasMouseOver = false;
        private bool isPressed = false;

        public Button()
        {
            this.slot = new Slot();

            InitializeComponent();
            rect.BorderBrush = null;
            FillBrush = new SolidColorBrush(Visual.Normal);
            rect.Background = FillBrush;

            UpdateVisual();
            UpdateCorners();
        }

        protected void UpdateVisual()
        {
            var fill = Visual.Normal;
            if (!IsEnabled) fill = Visual.Disabled;
            else if (isPressed) fill = Visual.Pressed;
            else if (hasMouseOver) fill = Visual.MouseOver;

            FillBrush.Color = fill;
        }

        protected void UpdateCorners()
        {
            double radius = rect.ActualHeight / 2;
            switch (Stumps)
            {
                case Stumps.None:
                    rect.CornerRadius = new CornerRadius(0);
                    rect.Padding = new Thickness(5, 0, 5, 0);
                    break;
                case Stumps.Left:
                    rect.CornerRadius = new CornerRadius(radius, 0, 0, radius);
                    rect.Padding = new Thickness(radius, 0, 5, 0);
                    break;
                case Stumps.Right:
                    rect.CornerRadius = new CornerRadius(0, radius, radius, 0);
                    rect.Padding = new Thickness(5, 0, radius, 0);
                    break;
                case Stumps.Both:
                    rect.CornerRadius = new CornerRadius(radius);
                    rect.Padding = new Thickness(radius, 0, radius, 0);
                    break;
            }
        }

        private void rect_MouseEnter(object sender, MouseEventArgs e)
        {
            hasMouseOver = true;
            UpdateVisual();
        }
        private void rect_MouseLeave(object sender, MouseEventArgs e)
        {
            hasMouseOver = false;
            UpdateVisual();
        }

        private void rect_MouseDown(object sender, MouseButtonEventArgs e)
        {
            isPressed = true;
            UpdateVisual();
        }
        private void rect_MouseUp(object sender, MouseButtonEventArgs e)
        {
            isPressed = false;
            UpdateVisual();
            // TODO: executar comando
            Console.WriteLine("BUTTON PRESSED!");
        }

        private void LCARSControl_IsEnabledChanged(object sender, DependencyPropertyChangedEventArgs e)
        {
            UpdateVisual();
        }

        private void LCARSControl_MouseEnter(object sender, MouseEventArgs e)
        {
            hasMouseOver = true;
            UpdateVisual();
        }

        private void LCARSControl_MouseLeave(object sender, MouseEventArgs e)
        {
            hasMouseOver = false;
            UpdateVisual();
        }

        private void LCARSControl_MouseDown(object sender, MouseButtonEventArgs e)
        {
            isPressed = true;
            UpdateVisual();
        }

        private void LCARSControl_MouseUp(object sender, MouseButtonEventArgs e)
        {
            isPressed = false;
            UpdateVisual();
            // TODO: executar comando
            Debug.WriteLine("BUTTON PRESSED!");
        }

        private void LCARSControl_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            // UpdateVisual();
            UpdateCorners();
        }
    }
}
