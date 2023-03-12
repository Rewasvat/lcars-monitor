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
using Newtonsoft.Json;

namespace LCARSMonitorWPF.Controls
{
    /// <summary>
    /// Interaction logic for Panel.xaml
    /// </summary>
    public partial class Panel : LCARSControl, ILCARSSingleContainer
    {
        [JsonProperty]
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

        [JsonProperty]
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

        [JsonProperty]
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

        [JsonProperty]
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

        [JsonProperty]
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

        public Slot ChildSlot { get; protected set; }
        public Canvas ChildrenCanvas => canvas;

        [JsonProperty]
        [IgnoreOnEditor]
        public LCARSControl? ChildControl
        {
            get { return ChildSlot.AttachedChild; }
            set { ChildSlot.AttachedChild = value; }
        }

        protected Elbow topRightCorner;
        protected Elbow topLeftCorner;
        protected Elbow bottomRightCorner;
        protected Elbow bottomLeftCorner;
        protected Button topBorder;
        protected Button bottomBorder;
        protected Button rightBorder;
        protected Button leftBorder;
        protected double outMargin = 5.0; // margin from border elements to control edge

        // METHODS
        public Panel()
        {
            InitializeComponent();

            topBorder = new Button();
            topBorder.Visibility = Visibility.Hidden;
            topBorder.UseFixedVisual = true;
            canvas.Children.Add(topBorder);

            bottomBorder = new Button();
            bottomBorder.Visibility = Visibility.Hidden;
            bottomBorder.UseFixedVisual = true;
            canvas.Children.Add(bottomBorder);

            rightBorder = new Button();
            rightBorder.Visibility = Visibility.Hidden;
            rightBorder.UseFixedVisual = true;
            rightBorder.Stumps = Stumps.None;
            canvas.Children.Add(rightBorder);

            leftBorder = new Button();
            leftBorder.Visibility = Visibility.Hidden;
            leftBorder.UseFixedVisual = true;
            leftBorder.Stumps = Stumps.None;
            canvas.Children.Add(leftBorder);

            topRightCorner = new Elbow();
            topRightCorner.ElbowType = ElbowType.TopRight;
            topRightCorner.Visibility = Visibility.Hidden;
            canvas.Children.Add(topRightCorner);

            topLeftCorner = new Elbow();
            topLeftCorner.ElbowType = ElbowType.TopLeft;
            topLeftCorner.Visibility = Visibility.Hidden;
            canvas.Children.Add(topLeftCorner);

            bottomRightCorner = new Elbow();
            bottomRightCorner.ElbowType = ElbowType.BottomRight;
            bottomRightCorner.Visibility = Visibility.Hidden;
            canvas.Children.Add(bottomRightCorner);

            bottomLeftCorner = new Elbow();
            bottomLeftCorner.ElbowType = ElbowType.BottomLeft;
            bottomLeftCorner.Visibility = Visibility.Hidden;
            canvas.Children.Add(bottomLeftCorner);

            ChildSlot = new Slot(this);

            UpdateBorders();
        }

        public void UpdateBorders()
        {
            UpdateBorderCornerElement(topRightCorner, ElbowType.TopRight);
            UpdateBorderCornerElement(topLeftCorner, ElbowType.TopLeft);
            UpdateBorderCornerElement(bottomRightCorner, ElbowType.BottomRight);
            UpdateBorderCornerElement(bottomLeftCorner, ElbowType.BottomLeft);

            UpdateBorderRectElement(topBorder, PanelBorders.Top);
            UpdateBorderRectElement(bottomBorder, PanelBorders.Bottom);
            UpdateBorderRectElement(leftBorder, PanelBorders.Left);
            UpdateBorderRectElement(rightBorder, PanelBorders.Right);

            UpdateInternalArea();
        }
        private static void BordersChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is Panel obj)
            {
                obj.UpdateBorders();
            }
        }

        public void UpdateBorderRectElement(Button border, PanelBorders type)
        {
            if (!Borders.HasFlag(type))
            {
                border.Visibility = Visibility.Hidden;
                border.Width = border.Height = 1;
                return;
            }

            border.VisualStyle = VisualStyle;
            border.Visibility = Visibility.Visible;
            var cornerSize = topRightCorner.BaseArea;
            double actualWidth = Math.Max(outMargin * 3 + cornerSize.Width * 2, ActualWidth);
            double actualHeight = Math.Max(outMargin * 3 + cornerSize.Height * 2, ActualHeight);

            if (type == PanelBorders.Top || type == PanelBorders.Bottom)
            {
                double left = outMargin;
                double right = actualWidth - outMargin;

                if (Borders.HasFlag(PanelBorders.Left))
                {
                    left += BorderWidth;
                }
                if (Borders.HasFlag(PanelBorders.Right))
                {
                    right -= BorderWidth;
                }

                border.Width = right - left;
                border.Height = BorderHeight;

                if (type == PanelBorders.Top)
                    border.SetValue(Canvas.TopProperty, outMargin);
                else
                    border.SetValue(Canvas.TopProperty, actualHeight - BorderHeight - outMargin);
                border.SetValue(Canvas.LeftProperty, left);
            }
            else
            {
                double top = outMargin;
                double bottom = actualHeight - outMargin;

                if (Borders.HasFlag(PanelBorders.Top))
                {
                    top += topLeftCorner.BaseArea.Height - 5;
                }
                if (Borders.HasFlag(PanelBorders.Bottom))
                {
                    bottom -= bottomRightCorner.BaseArea.Height - 5;
                }

                border.Width = BorderWidth;
                border.Height = bottom - top;

                if (type == PanelBorders.Left)
                    border.SetValue(Canvas.LeftProperty, outMargin);
                else
                    border.SetValue(Canvas.LeftProperty, actualWidth - BorderWidth - outMargin);
                border.SetValue(Canvas.TopProperty, top);
            }
        }

        public void UpdateBorderCornerElement(Elbow elbow, ElbowType type)
        {
            elbow.VisualStyle = VisualStyle;
            elbow.InnerArcRadius = BorderInnerRadius;
            elbow.Bar = BorderHeight;
            elbow.Column = BorderWidth;
            elbow.ElbowType = type;

            bool enabled = false;
            double x = 0.0;
            double y = 0.0;
            var size = elbow.BaseArea;
            double width = size.Width;
            double height = size.Height;
            switch (type)
            {
                case (ElbowType.TopRight):
                    enabled = Borders.HasFlag(PanelBorders.Top) && Borders.HasFlag(PanelBorders.Right);
                    x = ActualWidth - width - outMargin;
                    y = outMargin;
                    break;
                case (ElbowType.TopLeft):
                    enabled = Borders.HasFlag(PanelBorders.Top) && Borders.HasFlag(PanelBorders.Left);
                    x = y = outMargin;
                    break;
                case (ElbowType.BottomRight):
                    enabled = Borders.HasFlag(PanelBorders.Bottom) && Borders.HasFlag(PanelBorders.Right);
                    x = ActualWidth - width - outMargin;
                    y = ActualHeight - height - outMargin;
                    break;
                case (ElbowType.BottomLeft):
                    enabled = Borders.HasFlag(PanelBorders.Bottom) && Borders.HasFlag(PanelBorders.Left);
                    x = outMargin;
                    y = ActualHeight - height - outMargin;
                    break;
            }
            elbow.Visibility = enabled ? Visibility.Visible : Visibility.Hidden;

            elbow.Width = width;
            elbow.Height = height;
            elbow.SetValue(Canvas.LeftProperty, x);
            elbow.SetValue(Canvas.TopProperty, y);
        }

        public void UpdateInternalArea()
        {
            double slotWidth = ActualWidth - outMargin * 2;
            double slotHeight = ActualHeight - outMargin * 2;

            double x = outMargin;
            double y = outMargin;
            if (Borders.HasFlag(PanelBorders.Left))
            {
                x += topLeftCorner.ActualWidth;
                slotWidth -= topLeftCorner.ActualWidth;
            }
            if (Borders.HasFlag(PanelBorders.Top))
            {
                y += topLeftCorner.ActualHeight;
                slotHeight -= topLeftCorner.ActualHeight;
            }
            if (Borders.HasFlag(PanelBorders.Right))
            {
                slotWidth -= topLeftCorner.ActualWidth;
            }
            if (Borders.HasFlag(PanelBorders.Bottom))
            {
                slotHeight -= topLeftCorner.ActualHeight;
            }
            var rect = ChildSlot.Area;
            rect.X = x;
            rect.Y = y;
            rect.Width = Math.Max(10, slotWidth);
            rect.Height = Math.Max(10, slotHeight);
            ChildSlot.Area = rect;
        }

        private void LCARSControl_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            UpdateBorders();
        }

        private void LCARSControl_Initialized(object sender, EventArgs e)
        {

        }

        private void LCARSControl_Loaded(object sender, RoutedEventArgs e)
        {
            UpdateBorders();
        }

    }
}
