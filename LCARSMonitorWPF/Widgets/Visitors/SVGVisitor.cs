using LibreHardwareMonitor.Hardware;
using Svg;
//using SkiaSharp;
//using Svg.Skia;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;

namespace LCARSMonitor.Widgets.Visitors
{
    public class SVGVisitor : WidgetVisitor
    {
        private string svgPath;
        private Image box;

        public SVGVisitor(string svgPath)
        {
            this.svgPath = svgPath;
            box = new Image();
            View = box;

            box.IsEnabled = true;
            box.Width = box.Height = 200;
            UpdateImage();
        }

        private void UpdateImage()
        {
            var svgDoc = SvgDocument.Open(svgPath);
            System.Drawing.Bitmap svgImg = svgDoc.Draw((int)box.Width, (int)box.Height);

            IntPtr ip = svgImg.GetHbitmap();
            BitmapSource? bs = null;
            try
            {
                bs = System.Windows.Interop.Imaging.CreateBitmapSourceFromHBitmap(ip,
                   IntPtr.Zero, Int32Rect.Empty,
                   System.Windows.Media.Imaging.BitmapSizeOptions.FromEmptyOptions());
            }
            finally
            {
                DeleteObject(ip);
            }

            box.Source = bs;
        }

        [DllImport("gdi32")]
        static extern int DeleteObject(IntPtr o);

        public override void VisitSensor(ISensor sensor)
        {
        }
    }
}
