import json
import numpy as np

class SettingsLoadingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return "Errore durante il caricamento delle impostazioni."

class SettingsSavingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    def __str__(self) -> str:
        return "Errore durante il salvataggio delle impostazioni.."

class Property:

    TYPE_GENERIC = 0
    TYPE_BOOL = 1
    TYPE_INT_RANGE = 2
    TYPE_FLOAT_RANGE = 3
    TYPE_MULTIPLE_OPTIONS = 4

    def __init__(self, id, property_name = None, property_group = "default", type = 0, default=None, value=None) -> None:
        self.id = id
        self.property_name = property_name if property_name else self.id
        self.property_group = property_group
        self.type = type
        self.default = default
        if value:
            self.value = value
        else:
            self.value = self.default

    def set(self, value):
        self.value = value

    def to_dictionary(self):
        return {
            "id":self.id,
            "property_name":self.property_name,
            "property_group": self.property_group,
            "type":self.type,
            "default": self.default,
            "value":self.value
        }

    def from_dictionary(dict):
        return Property(dict["id"], dict["property_name"], dict["propert_group"], dict["type"], dict["default"], dict["value"])


class BoolProperty(Property):
    def __init__(self, id, name = None, default = False, value = None, group = "default") -> None:
        super().__init__(id, property_name=name, property_group=group, type=Property.TYPE_BOOL, default=default, value = value)

    def switch(self):
        self.value = not self.value

    def from_dictionary(dict):
        return BoolProperty(dict["id"], dict["property_name"], dict["default"], group=dict["property_group"])

    def __eq__(self, o: object) -> bool:
        return o != None and o.id == self.id

class FloatRangeProperty(Property):
    def __init__(self, id, name = None, min=0.0, max=1.0, resolution=0.1, default=None, value = None, group = "default") -> None:
        super().__init__(id, name, group, Property.TYPE_FLOAT_RANGE, default if default != None else min, value=value)
        self.min = min
        self.max = max
        self.resolution = resolution

    def set(self, value):
        self.value = min(self.max, max(self.min, float(value)))

    def to_dictionary(self):
        return {
            "id":self.id,
            "property_name":self.property_name,
            "property_group":self.property_group,
            "type":Property.TYPE_FLOAT_RANGE,
            "default": self.default,
            "value":self.value,
            "min":self.min,
            "max":self.max,
            "resolution":self.resolution
        }

    def from_dictionary(dict):
        prop = FloatRangeProperty(id = dict["id"], 
                                  name = dict["property_name"],
                                  min = dict["min"],
                                  max=dict["max"],
                                  resolution=dict["resolution"],
                                  default = dict["default"],
                                  group=dict["property_group"])
        prop.set(dict["value"])
        return prop


class IntRangeProperty(Property):
    def __init__(self, id, name = None, min=0, max=10, resolution=1, default=None, value = None, group = "default") -> None:
        super().__init__(id, name, group, Property.TYPE_INT_RANGE, default if default != None else min, value=value)
        self.min = min
        self.max = max
        self.resolution = resolution

    def set(self, value):
        self.value = min(self.max, max(self.min, int(value)))

    def to_dictionary(self):
        return {
            "id":self.id,
            "property_name":self.property_name,
            "propert_group":self.property_group,
            "type":Property.TYPE_INT_RANGE,
            "default": self.default,
            "value":self.value,
            "min":self.min,
            "max":self.max,
            "resolution":self.resolution
        }

    def from_dictionary(dict):
        prop = IntRangeProperty(id = dict["id"], 
                                  name = dict["property_name"],
                                  min = dict["min"],
                                  max=dict["max"],
                                  resolution=dict["resolution"],
                                  default = dict["default"],
                                  group=dict["property_group"])
        prop.set(dict["value"])
        return prop

class MultipleOptionsProperty(Property):
    def __init__(self, id, name = None, options=[], default = None, group = "default") -> None:
        super().__init__(id, name, group, Property.TYPE_MULTIPLE_OPTIONS, default, value=default)
        self.options = options

    def set(self, value):
        if value in self.options:
            self.value = value
        else:
            self.value = self.default

    def to_dictionary(self):
        return {
            "id":self.id,
            "property_name":self.property_name,
            "propert_group":self.property_group,
            "type":Property.TYPE_MULTIPLE_OPTIONS,
            "options": self.options,
            "default": self.default,
        }

    def from_dictionary(dict):
        prop = MultipleOptionsProperty(id = dict["id"], 
                                       name = dict["property_name"],
                                       options = dict["options"],
                                       default = dict["default"],
                                       group=dict["property_group"])
        return prop

class Color:
    def __init__(self, color_id, color_group, lower_value = [], upper_value = [], rgb=[]) -> None:
        self.color_id = color_id
        self.color_group = color_group
        if len(lower_value) < 3:
            lower_value = np.array([0, 70, 80])
        if len(upper_value) < 3:
            upper_value = np.array([0, 255, 255])
        if len(rgb) < 3:
            rgb = [30,30,30]
        self.lowerH = IntRangeProperty(color_id +"_lH", "lower H", min=0, max=255, value=int(lower_value[0]))
        self.lowerS = IntRangeProperty(color_id +"_lS", "lower S", min=0, max=255, value=int(lower_value[1]))
        self.lowerV = IntRangeProperty(color_id +"_lV", "lower V", min=0, max=255, value=int(lower_value[2]))
        self.upperH = IntRangeProperty(color_id +"_uH", "upper H", min=0, max=255, value=int(upper_value[0]))
        self.upperS = IntRangeProperty(color_id +"_uS", "upper S", min=0, max=255, value=int(upper_value[1]))
        self.upperV = IntRangeProperty(color_id +"_uV", "upper V", min=0, max=255, value=int(upper_value[2]))
        self.R = IntRangeProperty(color_id + "R", "R", min=0, max=255, value=rgb[0])
        self.G = IntRangeProperty(color_id + "G", "G", min=0, max=255, value=rgb[1])
        self.B = IntRangeProperty(color_id + "B", "B", min=0, max=255, value=rgb[2])

    def setId(self, id):
        self.color_id = id

    def setGroup(self, group):
        self.color_group = group

    def getProperties(self):
        return [self.lowerH, self.lowerS, self.lowerV, 
                self.upperH, self.upperS, self.upperV,
                self.R, self.G, self.B]

    def lowerHSV(self):
        return np.array([self.lowerH.value, self.lowerS.value, self.lowerV.value])
        
    def upperHSV(self):
        return np.array([self.upperH.value, self.upperS.value, self.upperV.value])

    def RGB(self):
        return [self.R.value, self.G.value, self.B.value]

    def BGR(self):
        return [self.B.value, self.G.value, self.R.value]

    def default():
        return Color("DEFAULT", "Default")

    def to_dictionary(self):
        return {
            "color_id" : self.color_id,
            "color_group" : self.color_group,
            "lower_value": self.lowerHSV().tolist(),
            "upper_value": self.upperHSV().tolist(),
            "rgb": self.RGB()
        }

    def from_dictionary(dict):
        return Color(color_id=dict["color_id"], color_group=dict["color_group"],
                    lower_value=dict["lower_value"], upper_value=dict["upper_value"],
                    rgb=dict["rgb"])
        

class Settings:

    DEFAULT_PATH = "settings/default.json"

    CAP_WIDTH = 640
    CAP_HEIGHT = 480

    COLORS = [Color.default()]

    PROPERTIES = [
            FloatRangeProperty("bright_gain", "Bright Gain", min=0.0, max=5.0, resolution=0.01, default=1.0, group="image_filtering"),
            IntRangeProperty("bright_offset", "Bright Offset", min=-255, max=255, resolution=1, default=0, group="image_filtering"),
            IntRangeProperty("blur_size", "Blur", min=1, max=100, resolution=2, default=1, group="image_filtering"),
            IntRangeProperty("min_contour_area", "Min. Area Contorno", min=0, max=10000, default=2000, group="block_properties"),
            FloatRangeProperty("max_edge_ratio", "Max. Rapporto Lati", min=1.0, max=5.0, resolution=0.1, default=1.4, group="block_properties"),
            IntRangeProperty("min_contour_completeness", "Min. Completezza Contorno", min=1, max=100, resolution=1, default=80, group="block_properties"),
            BoolProperty("subtract_contours", "Usa Sottrazione Contorni", default=True, group="detection_params"),
            IntRangeProperty("max_search_steps", "Max. Iterazioni", min=0, max=10, default=3, group="detection_params"),
            IntRangeProperty("contour_dilation", "Dilatazione Contorni", min=1, max=100, resolution=2, default=7, group="detection_params"),
            IntRangeProperty("contour_threshold", "Soglia Contorni", min=0, max=255, resolution=1, default=10, group="detection_params"),
            IntRangeProperty("close_size", "Chiusura", min=1, max=100, resolution=2, default=3, group="detection_params"),
            FloatRangeProperty("ca_scale_factor", "Fattore di Scala Min. Area Cont.", min=0.1, max=1.0, resolution=0.1, default=0.9, group="detection_params"),
            FloatRangeProperty("cd_scale_factor", "Fattore di Scala Dilatazione", min=1.0, max=2.0, resolution=0.1, default=1.5, group="detection_params"),
            MultipleOptionsProperty("algorithm", "Algoritmo", options=["Breadth First Tree Search",
                                                                                "Breadth First Graph Search",
                                                                                "Depth First Tree Search",
                                                                                "Depth First Graph Search",
                                                                                "Iterative Depth First Search",
                                                                                "A* Search"], 
                                                default="Breadth First Tree Search", 
                                                group="model_properties"),
            MultipleOptionsProperty("goal_type", "Goal", options=["Default", "Custom"], 
                                    default="Default", 
                                    group="model_properties")
    ]

    def addColor(color):
        Settings.COLORS.append(color)

    def removeColor(color):
        Settings.COLORS.remove(color)

    def propValues():
        values = {}
        for p in Settings.PROPERTIES:
            values[p.id] = p.value
        return values

    def getPropertyByID(id):
        prop = [p for p in Settings.PROPERTIES if p.id == id]
        if prop != None and len(prop) > 0:
            return prop[0]
        return None

    def getPropertiesByGroup(group):
        return [p for p in Settings.PROPERTIES if p.property_group == group]

    def getColorByID(id):
        col = [c for c in Settings.COLORS if c.color_id == id]
        return col[0] if len(col) > 0 else None

    def loadFromFile(filename = "settings/default.json"):
        try:
            with open(filename, "r") as sett_file:
                properties = json.load(sett_file)
                colors = properties["colors"]
                cap_prop = properties["properties"]

                Settings.COLORS.clear()
                for color in colors:
                    Settings.COLORS.append(Color.from_dictionary(color))

                for property in cap_prop:
                    p = Settings.getPropertyByID(property)
                    if p != None:
                        p.set(cap_prop[property])
        except:
            raise SettingsLoadingException()

    def save(filename = "settings/settings.json"):
        try:
            with open(filename, "w") as outfile:
                json.dump({
                    "colors" : [c.to_dictionary() for c in Settings.COLORS],
                    "properties" : Settings.propValues()
                }, outfile)
        except:
            raise SettingsSavingException()