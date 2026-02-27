from enum import Enum

from aam_py.error import AamlError, NotFoundError, InvalidValueError
from aam_py.types import Type
from aam_py.types.primitive_type import PrimitiveType

PHYSICS_TYPES_MAP = {
    # Base SI Units
    "meter": "Meter",
    "kilogram": "Kilogram",
    "second": "Second",
    "ampere": "Ampere",
    "kelvin": "Kelvin",
    "mole": "Mole",
    "candela": "Candela",

    # Geometry and Space
    "squaremeter": "SquareMeter",
    "cubicmeter": "CubicMeter",
    "radian": "Radian",
    "steradian": "Steradian",
    "arcdegree": "ArcDegree",
    "arcminute": "ArcMinute",
    "arcsecond": "ArcSecond",
    "angstrom": "Angstrom",
    "inversemeter": "InverseMeter",

    # Mechanics and Motion
    "meterpersecond": "MeterPerSecond",
    "meterpersecondsquared": "MeterPerSecondSquared",
    "radianpersecond": "RadianPerSecond",
    "radianpersecondsquared": "RadianPerSecondSquared",
    "newton": "Newton",
    "newtonmeter": "NewtonMeter",
    "pascal": "Pascal",
    "joule": "Joule",
    "watt": "Watt",
    "hertz": "Hertz",
    "kilogrampercubicmeter": "KilogramPerCubicMeter",
    "kilogrammeterpersecond": "KilogramMeterPerSecond",
    "newtonpermeter": "NewtonPerMeter",
    "kilogramsquaremeter": "KilogramSquareMeter",
    "pascalsecond": "PascalSecond",
    "squaremeterpersecond": "SquareMeterPerSecond",
    "newtonsecond": "NewtonSecond",
    "newtonpercubicmeter": "NewtonPerCubicMeter",
    "joulesecond": "JouleSecond",
    "meterpercubicsecond": "MeterPerCubicSecond",
    "kilogrampersecond": "KilogramPerSecond",
    "cubicmeterpersecond": "CubicMeterPerSecond",
    "newtonpermetersquared": "NewtonPerMeterSquared",

    # Electricity and Magnetism
    "coulomb": "Coulomb",
    "volt": "Volt",
    "ohm": "Ohm",
    "ohmmeter": "OhmMeter",
    "farad": "Farad",
    "voltpermeter": "VoltPerMeter",
    "tesla": "Tesla",
    "weber": "Weber",
    "henry": "Henry",
    "siemens": "Siemens",
    "coulombpercubicmeter": "CoulombPerCubicMeter",
    "coulombpersquaremeter": "CoulombPerSquareMeter",
    "faradpermeter": "FaradPerMeter",
    "henrypermeter": "HenryPerMeter",
    "amperepermeter": "AmperePerMeter",
    "amperepersquaremeter": "AmperePerSquareMeter",
    "newtonpercoulomb": "NewtonPerCoulomb",
    "weberpermeter": "WeberPerMeter",
    "teslasquaremeter": "TeslaSquareMeter",

    # Thermodynamics
    "jouleperkilogramkelvin": "JoulePerKilogramKelvin",
    "jouleperkilogram": "JoulePerKilogram",
    "jouleperkelvin": "JoulePerKelvin",
    "voltperkelvin": "VoltPerKelvin",
    "wattpermeterkelvin": "WattPerMeterKelvin",
    "joulepermolekelvin": "JoulePerMoleKelvin",
    "kelvinperwatt": "KelvinPerWatt",
    "celsius": "Celsius",
    "fahrenheit": "Fahrenheit",
    "rankine": "Rankine",

    # Chemistry and Particles
    "kilogrampermole": "KilogramPerMole",
    "cubicmeterperkilogram": "CubicMeterPerKilogram",
    "katal": "Katal",
    "molepercubicmeter": "MolePerCubicMeter",
    "joulepermole": "JoulePerMole",
    "atomicmassunit": "Dalton", 
    "dalton": "Dalton", 
    "barn": "Barn",

    # Optics and Radiation
    "dioptre": "Dioptre",
    "becquerel": "Becquerel",
    "gray": "Gray",
    "sievert": "Sievert",
    "electronvolt": "ElectronVolt",
    "lumen": "Lumen",
    "lux": "Lux",
    "lumensecond": "LumenSecond",
    "candelapersquaremeter": "CandelaPerSquareMeter",
    "wattpersteradian": "WattPerSteradian",
    "wattpersquaremeter": "WattPerSquareMeter",
    "joulepersquaremeter": "JoulePerSquareMeter",
    "curie": "Curie",
    "roentgen": "Roentgen",
    "rutherford": "Rutherford",

    # Astronomy
    "lightyear": "LightYear",
    "parsec": "Parsec",
    "astronomicalunit": "AstronomicalUnit",
    "hubbleconstant": "HubbleConstant",
    "jansky": "Jansky",

    # Computing
    "bit": "Bit",
    "byte": "Byte",
    "baud": "Baud",
    "erlang": "Erlang",

    # Miscellaneous and Non-SI Units
    "dimensionless": "Dimensionless",
    "percentage": "Percentage",
    "decibel": "Decibel",
    "bar": "Bar",
    "millimeterofmercury": "MillimeterOfMercury",
    "atmosphere": "Atmosphere",
    "torr": "Torr",
    "poise": "Poise",
    "stokes": "Stokes",
    "sverdrup": "Sverdrup",
    "rayl": "Rayl",
    "gal": "Gal",
    "maxwell": "Maxwell",
    "gauss": "Gauss",
    "oersted": "Oersted",
    "gilbert": "Gilbert",
    "franklin": "Franklin",
    "debye": "Debye",
    "lambert": "Lambert",
    "phot": "Phot",
    "stilb": "Stilb",
    "kayser": "Kayser",
    "calorie": "Calorie",
    "britishthermalunit": "BritishThermalUnit",
    "langley": "Langley",
    "fermi": "Fermi",
    "metabolicequivalent": "MetabolicEquivalent",
    "machnumber": "MachNumber",
    "knots": "Knots",
    "nauticalmile": "NauticalMile",
    "horsepower": "Horsepower"
}

class PhysicsTypes(Type):
    __slots__ = ('name',)

    def __init__(self, name: str):
        self.name = name

    @classmethod
    def from_name(cls, name: str) -> 'Type':
        search = name.lower().replace('_', '').replace('-', '')
        if search in PHYSICS_TYPES_MAP:
            return cls(PHYSICS_TYPES_MAP[search])
        raise NotFoundError(name)

    def base_type(self) -> 'PrimitiveType':
        if self.name in ("Bit", "Byte", "Baud"):
            return PrimitiveType.I32
        return PrimitiveType.F64

    def validate(self, value: str) -> None:
        base = self.base_type()
        if base == PrimitiveType.I32:
            try:
                int(value)
            except ValueError:
                raise InvalidValueError(f"Expected integer for unit {self.name}, got '{value}'")
        elif base == PrimitiveType.F64:
            try:
                float(value)
            except ValueError:
                raise InvalidValueError(f"Expected number for unit {self.name}, got '{value}'")
        else:
            raise InvalidValueError(f"Unsupported base type for unit {self.name}")

    def __str__(self):
        # Return snake_case version possibly if requested, but for simplicity matching rust output
        # Rust format is the variant name formatted with camelCase
        return self.name[0].lower() + self.name[1:]
