using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Controls;
using LCARSMonitor.LCARS;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;

namespace LCARSMonitorWPF.Controls
{
    [JsonObject(MemberSerialization.OptIn)]
    public abstract class LCARSControl : UserControl
    {
        [JsonProperty]
        public string ID
        {
            get { return Name; }
            set
            {
                LCARSSystem.Global.UpdateControlID(this, value);
            }
        }

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

        public static LCARSControl? DeserializeJSON(string jsonData)
        {
            var settings = new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.All };
            return JsonConvert.DeserializeObject(jsonData, settings) as LCARSControl;
        }
        public static LCARSControl? DeserializeJsonFile(string filePath)
        {
            string jsonData = File.ReadAllText(filePath);
            return DeserializeJSON(jsonData);
        }

        public void SerializeIntoJsonFile(string filePath)
        {
            var settings = new JsonSerializerSettings { TypeNameHandling = TypeNameHandling.All };
            // string jsonData = JsonConvert.SerializeObject(lcarsData, Formatting.Indented, settings);

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
                        serializer.Serialize(jw, this);
                    }
                }
            }
        }
    }

    public class IgnoreOnEditorAttribute : Attribute { }

    public class EditorValidatorAttribute : Attribute
    {
        public string? Validator { get; set; }

        public EditorValidatorAttribute(string? validatorName)
        {
            Validator = validatorName;
        }

        public bool? CheckValidator(object obj)
        {
            if (Validator == null)
                return null;

            var methodInfo = obj.GetType().GetMethod(Validator);
            if (methodInfo == null)
                return null;

            return methodInfo.Invoke(obj, null) as bool?;
        }
    }
}
