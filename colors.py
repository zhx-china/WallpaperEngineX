import settings


DarkCon = "1e1f22"
DarkBac = "191a1c"

LightCon = "FFFFFF"
LightBac = "F5F5F5"

def GetColor(type = "bac"):
    if type == "bac":
        if settings.topic == 0:
            return LightBac
        elif settings.topic == 1:
            return DarkBac
    elif type == "con":
        if settings.topic == 0:
            return LightCon
        elif settings.topic == 1:
            return DarkCon
