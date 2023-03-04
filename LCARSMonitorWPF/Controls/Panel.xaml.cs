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
    /// Interaction logic for Panel.xaml
    /// </summary>
    public partial class Panel : LCARSControl
    {
        public Visuals VisualStyle
        {
            get { return (Visuals)GetValue(VisualStyleProperty); }
            set { SetValue(VisualStyleProperty, value); }
        }
        public static readonly DependencyProperty VisualStyleProperty = DependencyProperty.Register(
            "VisualStyle",
            typeof(Visuals),
            typeof(Panel),
            new PropertyMetadata(Visuals.Common, BordersChanged)
        );

        public PanelBorders Borders
        {
            get { return (PanelBorders)GetValue(BordersProperty); }
            set { SetValue(BordersProperty, value); }
        }
        public static readonly DependencyProperty BordersProperty = DependencyProperty.Register(
            "Borders",
            typeof(PanelBorders),
            typeof(Panel),
            new PropertyMetadata(PanelBorders.None, BordersChanged)
        );

        public double BorderHeight
        {
            get { return (double)GetValue(BorderHeightProperty); }
            set { SetValue(BorderHeightProperty, value); }
        }
        public static readonly DependencyProperty BorderHeightProperty = DependencyProperty.Register(
            "BorderHeight",
            typeof(double),
            typeof(Panel),
            new PropertyMetadata(50.0, BordersChanged)
        );

        public double BorderWidth
        {
            get { return (double)GetValue(BorderWidthProperty); }
            set { SetValue(BorderWidthProperty, value); }
        }
        public static readonly DependencyProperty BorderWidthProperty = DependencyProperty.Register(
            "BorderWidth",
            typeof(double),
            typeof(Panel),
            new PropertyMetadata(200.0, BordersChanged)
        );

        public double BorderInnerRadius
        {
            get { return (double)GetValue(BorderInnerRadiusProperty); }
            set { SetValue(BorderInnerRadiusProperty, value); }
        }
        public static readonly DependencyProperty BorderInnerRadiusProperty = DependencyProperty.Register(
            "BorderInnerRadius",
            typeof(double),
            typeof(Panel),
            new PropertyMetadata(30.0, BordersChanged)
        );

        protected Elbow? topRightCorner;
        protected Elbow? topLeftCorner;
        protected Elbow? bottomRightCorner;
        protected Elbow? bottomLeftCorner;
        protected Button? topBorder;
        protected Button? bottomBorder;
        protected Button? rightBorder;
        protected Button? leftBorder;

        // METHODS
        public Panel()
        {
            InitializeComponent();
        }

        public void UpdateBorders()
        {
            if (Borders.HasFlag(PanelBorders.Top))
            {

            }
        }
        private static void BordersChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is Panel obj)
            {
                obj.UpdateBorders();
            }
        }
    }
}
