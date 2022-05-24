from enum import Enum

class Crashcase(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj
    
    TYPE1 = (1, 'Zusammenstoß mit anfahrendem/ anhaltendem/ruhendem Fahrzeug')
    TYPE2 = (2, 'Zusammenstoß mit vorausfahrendem / wartendem Fahrzeug')
    TYPE3 = (3, 'Zusammenstoß mit seitlich in gleicher Richtung fahrendem Fahrzeug')
    TYPE4 = (4, 'Zusammenstoß mit entgegenkommendem Fahrzeug')
    TYPE5 = (5, 'Zusammenstoß mit einbiegendem / kreuzendem Fahrzeug')
    TYPE6 = (6, 'Zusammenstoß zwischen Fahrzeug und Fußgänger')
    TYPE7 = (7, 'Aufprall auf Fahrbahnhindernis')
    TYPE8 = (8, 'Abkommen von Fahrbahn nach rechts')
    TYPE9 = (9, 'Abkommen von Fahrbahn nach links')
    TYPE0 = (0, 'Unfall anderer Art')

class Crashtype(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj
    
    TYPE1 = (1, 'Fahrunfall')
    TYPE2 = (2, 'Abbiegunfall')
    TYPE3 = (3, 'Einbiegen / Kreuzen-Unfall')
    TYPE4 = (4, 'Überschreiten-Unfall')
    TYPE5 = (5, 'Unfall durch ruhenden Verkehr')
    TYPE6 = (6, 'Unfall mit Längsverkehr')
    TYPE7 = (7, 'Sonstiger Unfall')

class Month(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj
        
    TYPE1 = (1, 'Januar')
    TYPE2 = (2, 'Februar')
    TYPE3 = (3, 'März')
    TYPE4 = (4, 'April')
    TYPE5 = (5, 'Mai')
    TYPE6 = (6, 'Juni')
    TYPE7 = (7, 'Juli')
    TYPE8 = (8, 'August')
    TYPE9 = (9, 'September')
    TYPE10 = (10, 'Oktober')
    TYPE11 = (11, 'November')
    TYPE12 = (12, 'Dezember')

class Weekday(int, Enum):
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj
    
    TYPE1 = (1, 'Sonntag')
    TYPE2 = (2, 'Dienstag')
    TYPE3 = (3, 'Mittwoch')
    TYPE4 = (4, 'Donnerstag')
    TYPE5 = (5, 'Freitag')
    TYPE6 = (6, 'Samstag')
    TYPE7 = (7, 'Sonntag')

if __name__ == "__main__":
    print(Crashtype.TYPE1.label)