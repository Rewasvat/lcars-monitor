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
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace cu
{
    /// <summary>
    /// Interaction logic for UserControl1.xaml
    /// </summary>
    public partial class UserControl1 : UserControl
    {
        public UserControl1()
        {
            InitializeComponent();

            //Storyboard sb = (< YourNamespace >.Properties.Resources["BotRotation"] as Storyboard);
            Storyboard? sb = Resources["Storyboard1"] as Storyboard;
            sb?.Begin();
        }

        private void Storyboard_Completed(object sender, EventArgs e)
        {
            Storyboard? sb = Resources["Storyboard1"] as Storyboard;
            sb?.Begin();
        }
    }
}
