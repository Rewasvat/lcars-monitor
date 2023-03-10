using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Markup;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace LCARSMonitorWPF.Controls
{
    /// <summary>
    /// Interaction logic for Elbow.xaml
    /// </summary>
    public partial class Elbow : LCARSControl
    {
        // PROPERTIES
        private ElbowType type;
        public ElbowType ElbowType
        {
            // This is not a DependencyProperty on purpose.
            // The value never changed (stayed always on default) when used as DP, and I could't fix it, so...
            get { return type; }
            set
            {
                type = value;
                UpdatePath();
            }
        }

        public double Bar
        {
            get { return (double)GetValue(BarProperty); }
            set { SetValue(BarProperty, value); }
        }
        public static readonly DependencyProperty BarProperty = DependencyProperty.Register(
            "Bar",
            typeof(double),
            typeof(Elbow),
            new PropertyMetadata(50.0, UpdatePathCallback)
        );

        public double Column
        {
            get { return (double)GetValue(ColumnProperty); }
            set { SetValue(ColumnProperty, value); }
        }
        public static readonly DependencyProperty ColumnProperty = DependencyProperty.Register(
            "Column",
            typeof(double),
            typeof(Elbow),
            new PropertyMetadata(200.0, UpdatePathCallback)
        );

        public double InnerArcRadius
        {
            get { return (double)GetValue(InnerArcRadiusProperty); }
            set { SetValue(InnerArcRadiusProperty, value); }
        }
        public static readonly DependencyProperty InnerArcRadiusProperty = DependencyProperty.Register(
            "InnerArcRadius",
            typeof(double),
            typeof(Elbow),
            new PropertyMetadata(30.0, UpdatePathCallback)
        );

        public Visuals VisualStyle
        {
            get { return (Visuals)GetValue(VisualStyleProperty); }
            set { SetValue(VisualStyleProperty, value); }
        }
        public static readonly DependencyProperty VisualStyleProperty = DependencyProperty.Register(
            "VisualStyle",
            typeof(Visuals),
            typeof(Elbow),
            new PropertyMetadata(Visuals.Common, StyleChanged)
        );
        private static void StyleChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            if (d is Elbow obj)
            {
                obj.UpdateVisual();
            }
        }

        public Visual Visual
        {
            get { return Visual.GetVisual(VisualStyle); }
        }

        public Size BaseArea
        {
            get
            {
                return geometry.Bounds.Size;
            }
        }

        private PathGeometry geometry;

        // METHODS
        public Elbow()
        {
            InitializeComponent();
            this.DataContext = this;
            geometry = new PathGeometry();
            geometry.FillRule = FillRule.Nonzero;
            UpdatePath();
            UpdateVisual();
        }

        private void UpdatePath()
        {
            double big = InnerArcRadius + Math.Min(Bar, Column);
            double small = InnerArcRadius;

            string geo = string.Empty;
            // Geometry syntax ()
            // m = start(x,y)
            // a = arc(sizeXY, angle, isLargerThan180, sweepDirection, endXY)
            // l = line(x, y)
            // z = end
            switch (this.ElbowType)
            {
                case ElbowType.TopLeft:
                    geo = $"M0,{Bar + small} l{Column},0 a {small},{small} 90 0 1 {small},{-small} l 0,{-Bar} l {-Column - small + big},0 a {big},{big} 90 0 0 {-big},{big} z";
                    break;
                case ElbowType.TopRight:
                    geo = $"M{Column + small},{Bar + small} l{-Column},0 a {small},{small} 90 0 0 {-small},{-small} l 0,{-Bar} l {Column + small - big},0 a {big},{big} 90 0 1 {big},{big} z";
                    break;
                case ElbowType.BottomRight:
                    geo = $"M{Column + small},0 l{-Column},0 a {small},{small} 90 0 1 {-small},{small} l 0,{Bar} l {Column + small - big},0 a {big},{big} 90 0 0 {big},{-big} z";
                    break;
                case ElbowType.BottomLeft:
                    geo = $"M0,0 l{Column},0 a {small},{small} 90 0 0 {small},{small} l 0,{Bar} l {-Column - small + big},0 a {big},{big} 90 0 1 {-big},{-big} z";
                    break;
            }

            geometry.Clear();
            PathFigureCollectionConverter pfcc = new PathFigureCollectionConverter();
            geometry.Figures = pfcc.ConvertFrom(geo) as PathFigureCollection;

            path.Data = geometry;
            mask.Data = geometry;
        }

        private void UpdateVisual()
        {
            path.Fill = Visual.NormalBrush;
        }

        private static void UpdatePathCallback(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            (d as Elbow)?.UpdatePath();
        }

        ////  SERIALIZATION

        protected override LCARSControlData CreateDataObject()
        {
            return new ElbowData
            {
                VisualStyle = VisualStyle,
                ElbowType = ElbowType,
                Bar = Bar,
                Column = Column,
                InnerArcRadius = InnerArcRadius,
            };
        }

        protected override void LoadDataInternal(LCARSControlData baseData)
        {
            var data = baseData as ElbowData;
            if (data == null)
                return;
            VisualStyle = data.VisualStyle;
            ElbowType = data.ElbowType;
            Bar = data.Bar;
            Column = data.Column;
            InnerArcRadius = data.InnerArcRadius;
        }
    }

    public class ElbowData : LCARSControlData
    {
        public Visuals VisualStyle { get; set; }
        public ElbowType ElbowType { get; set; }
        public double Bar { get; set; }
        public double Column { get; set; }
        public double InnerArcRadius { get; set; }
    }
}
