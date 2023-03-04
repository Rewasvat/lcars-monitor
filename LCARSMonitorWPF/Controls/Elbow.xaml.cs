using System;
using System.Collections.Generic;
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
        public ElbowType ElbowType
        {
            get { return (ElbowType)GetValue(ElbowTypeProperty); }
            set { SetValue(ElbowTypeProperty, value); }
        }
        public static readonly DependencyProperty ElbowTypeProperty = DependencyProperty.Register(
            "ElbowType",
            typeof(ElbowType),
            typeof(Button),
            new PropertyMetadata(ElbowType.TopRight, UpdatePathCallback)
        );

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

        // TODO: property pra Visual/cor
        public Brush Fill
        {
            get { return (Brush)GetValue(FillProperty); }
            set { SetValue(FillProperty, value); }
        }

        public static readonly DependencyProperty FillProperty = DependencyProperty.Register("Fill", typeof(Brush),
            typeof(Elbow), new PropertyMetadata(new SolidColorBrush(Colors.White)));

        // METHODS
        public Elbow()
        {
            InitializeComponent();
            this.DataContext = this;
            UpdatePath();
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
            switch (ElbowType)
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

            PathGeometry pathGeo = new PathGeometry();
            pathGeo.FillRule = FillRule.Nonzero;
            PathFigureCollectionConverter pfcc = new PathFigureCollectionConverter();
            pathGeo.Figures = pfcc.ConvertFrom(geo) as PathFigureCollection;

            path.Data = pathGeo;
            mask.Data = pathGeo;
        }

        private static void UpdatePathCallback(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            (d as Elbow)?.UpdatePath();
        }
    }
}
