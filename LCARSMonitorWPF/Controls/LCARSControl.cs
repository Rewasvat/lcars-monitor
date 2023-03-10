using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;
using LCARSMonitor.LCARS;
using Newtonsoft.Json;

namespace LCARSMonitorWPF.Controls
{
    public abstract class LCARSControl : UserControl
    {
        public virtual void OnAttachToSlot(Slot? slot)
        {
            // NOTE: this assumes parent object is always a Canvas (this is true for Panel, but what about other containers?)
            if (slot != null)
            {
                IsEnabled = true;
                Visibility = System.Windows.Visibility.Visible;

                var rect = slot.Area;
                SetValue(Canvas.LeftProperty, rect.Left);
                SetValue(Canvas.TopProperty, rect.Top);
                Width = Math.Max(10, rect.Width);
                Height = Math.Max(10, rect.Height);
            }
            else
            {
                IsEnabled = false;
                Visibility = System.Windows.Visibility.Hidden;
            }
        }

        public LCARSControl()
        {
            LCARSSystem.Global.RegisterControl(this);
        }

        ////  SERIALIZATION

        protected virtual LCARSControlData CreateDataObject()
        {
            throw new NotImplementedException();
        }

        protected virtual void LoadDataInternal(LCARSControlData data)
        {
            throw new NotImplementedException();
        }

        public LCARSControlData Serialize()
        {
            var data = CreateDataObject();
            data.Type = this.GetType().FullName;
            data.Name = Name;
            return data;
        }

        public void LoadData(LCARSControlData data)
        {
            Name = data.Name;
            LoadDataInternal(data);
        }

        public static LCARSControl? Deserialize(LCARSControlData? data)
        {
            if (data == null)
                return null;
            if (data.Type == null)
            {
                throw new ArgumentException();
            }
            Type? ControlType = Type.GetType(data.Type);
            if (ControlType == null)
            {
                throw new ArgumentException();
            }

            LCARSControl? control = Activator.CreateInstance(ControlType) as LCARSControl;
            control?.LoadData(data);
            return control;
        }

        public static LCARSControl? DeserializeJSON(string jsonData)
        {
            var settings = new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.All };
            LCARSControlData? lcarsData = JsonConvert.DeserializeObject(jsonData, settings) as LCARSControlData;
            return Deserialize(lcarsData);
        }
        public static LCARSControl? DeserializeJsonFile(string filePath)
        {
            string jsonData = File.ReadAllText(filePath);
            return DeserializeJSON(jsonData);
        }

        public void SerializeIntoJsonFile(string filePath)
        {
            var settings = new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.All };
            var lcarsData = Serialize();
            string jsonData = JsonConvert.SerializeObject(lcarsData, Formatting.Indented, settings);

            using (FileStream fs = File.Open(filePath, FileMode.OpenOrCreate))
            {
                using (StreamWriter sw = new StreamWriter(fs))
                {
                    using (JsonTextWriter jw = new JsonTextWriter(sw))
                    {
                        jw.Formatting = Formatting.Indented;
                        jw.IndentChar = ' ';
                        jw.Indentation = 4;

                        JsonSerializer serializer = new JsonSerializer();
                        serializer.TypeNameHandling = TypeNameHandling.All;
                        serializer.Serialize(jw, lcarsData);
                    }
                }
            }
        }
    }

    public class LCARSControlData
    {
        public string? Type { get; set; }
        public string? Name { get; set; }
    }
}
