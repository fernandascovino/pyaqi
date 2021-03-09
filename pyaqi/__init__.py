import math
import warnings
import yaml

from aqi_references import * # current: brazil_reference

warnings.simplefilter('always', UserWarning)

class aqi:
    def __init__(self):
        # poluents
        self.poluents = {
            "pm10_24h": dict(),
            "pm25_24h": dict(),
            "o3_8h": dict(),
            "co_8h": dict(),
            "no2_1h": dict(),
            "so2_24h": dict()
        }

        # aqi reference values
        self.aqi_brazil = dict()
        for pol, values in brazil_reference["poluents"].items():
            self.aqi_brazil[pol] = dict(zip(values, brazil_reference["aqi"]))
        
    def normalize_value(self, value, pol, algo=None):
        if algo == self.aqi_brazil:
            if pol == "co_8h" and type(value) == int:
                warnings.warn("Monóxido de carbono (CO) sempre é apresentado com uma casa após a vírgula (float). Caso o valor esteja arredondado, rodar novamente com o valor correto.")
                return round(value, 1)
            if pol != "co_8h" and type(value) == float:
                warnings.warn("Poluente deve ser apresentado passado como inteiro. Arredondamento feito para inteiro ou par (quando X.5) mais próximo.")
                if Decimal(str(value)) % 1 == 0.5:
                    lower, upper = math.floor(value), math.ceil(value)
                    if lower ** 2 == 0: 
                        return int(lower)
                    else: 
                        return int(upper)
                return int(value)
            else: 
                return value
        
    def get_bounds(self, value, pol, algo=None):
        """
        Calcula o intervalo de referência ao qual o poluente pertence dado sua concentração média.
        
        Args:
            value (int): Concentração média do poluente em 24h/8h/1h (ver referência de cada poluente).
            pol (string): Poluente indicado para cálculo. Escolher dentre:
                
                * "pm10_24h", "pm25_24h", "o3_8h", "co_8h", "no2_1h", "so2_24h"
                
            algo (self.mode): Algoritmo escolhido para cálculo. Disponíveis:
                
                * self.aqi_brazil
                
        Returns:
            tuple: Intervalo de referência do poluente dada sua concentração média.
        """
        # set deafault algo
        if not algo: algo = self.aqi_brazil
        # check for values already calculated
        if ("pol_bounds" in self.poluents[pol].keys()) and (self.poluents[pol]["value"] == value):
            return self.poluents[pol]["pol_bounds"]
        # calculate values
        else:
            self.poluents[pol]["value"] = self.normalize_value(value, pol, algo)
            ranges = algo[pol].keys()

            for (lower, upper) in ranges:
                if lower <= self.poluents[pol]["value"] <= upper:
                    self.poluents[pol]["pol_bounds"] = (lower, upper)
                    return self.poluents[pol]["pol_bounds"]
        

    def get_aqi_bounds(self, value, pol, algo=None):
        """
        Calcula o intervalo do índice ao qual o poluente pertence dado sua concentração média.
        
        Args:
            value (int): Concentração média do poluente em 24h/8h/1h (ver referência de cada poluente).
            pol (string): Poluente indicado para cálculo. Escolher dentre:
                
                * "pm10_24h", "pm25_24h", "o3_8h", "co_8h", "no2_1h", "so2_24h"
                
            algo (self.mode): Algoritmo escolhido para cálculo. Disponíveis:
                
                * self.aqi_brazil
                
        Returns:
            tuple: Intervalo do índice referente ao poluente dada sua concentração média.
        """
        # set deafault algo
        if not algo: algo = self.aqi_brazil
        # check for values already calculated
        if ("aqi_bounds" in self.poluents[pol].keys()) and (self.poluents[pol]["value"] == value):
            return self.poluents[pol]["aqi_bounds"]
        else:
            self.poluents[pol]["pol_bounds"] = self.get_bounds(value, pol, algo)
            self.poluents[pol]["aqi_bounds"] = algo[pol][self.poluents[pol]["pol_bounds"]]
            return self.poluents[pol]["aqi_bounds"]
        
    def get_iaqi(self, value, pol, algo=None):
        """
        Calcula o índice de qualidade intermediário, i.e. somente de um poluente, dado sua concentração média.
        
        Args:
            value (int, float): Concentração média do poluente em 24h/8h/1h (ver referência de cada poluente). 
                Monóxido de carbono (CO) sempre é apresentado com uma casa após a vírgula (float), os demais poluentes inteiros (int).
            pol (string): Poluente indicado para cálculo. Escolher dentre:
                
                * "pm10_24h", "pm25_24h", "o3_8h", "co_8h", "no2_1h", "so2_24h"
                
            algo (self.mode): Algoritmo escolhido para cálculo. Disponíveis:
                
                * self.aqi_brazil
                
        Returns:
            int: Índice de qualidade intermediário do poluente dada sua concentração média.
        """
        # set deafault algo
        if not algo: algo = self.aqi_brazil
        # check for values already calculated
        if ("aqi_value" in self.poluents[pol].keys()) and (self.poluents[pol]["value"] == value):
            return self.poluents[pol]["aqi_value"]
        # calculate values
        else:
            self.poluents[pol]["pol_bounds"] = self.get_bounds(value, pol, algo)
            print("Intervalo do poluente:", self.poluents[pol]["pol_bounds"])
            
            self.poluents[pol]["aqi_bounds"] = algo[pol][self.poluents[pol]["pol_bounds"]]
            print("Intervalo de referência do aqi:", self.poluents[pol]["aqi_bounds"])
            
            self.poluents[pol]["aqi_value"] = int(
                self.poluents[pol]["aqi_bounds"][0]
                + (
                    (self.poluents[pol]["aqi_bounds"][1] - self.poluents[pol]["aqi_bounds"][0])
                    /(self.poluents[pol]["pol_bounds"][1] - self.poluents[pol]["pol_bounds"][0])
                )
                * (self.poluents[pol]["value"] - self.poluents[pol]["pol_bounds"][0])
            )
        
            return self.poluents[pol]["aqi_value"]
        
    def get_aqi(self, values=None, algo=None):
        """
        Calcula o índice de qualidade do ar dados os poluentes especificados.
        
        Args:
            values (dict): Concentração média de cada poluente em 24h/8h/1h (ver referência de cada poluente). 
            
            Os poluentes referentes de cada algoritmo são:
                
                * self.aqi_brazil: "pm10_24h", "pm25_24h", "o3_8h", "co_8h", "no2_1h", "so2_24h"
                
            algo (self.mode): Algoritmo escolhido para cálculo. Disponíveis:
                
                * self.aqi_brazil
                
        Returns:
            int: Índice de qualidade do ar.
        """
        # set deafault algo
        if not algo: algo = self.aqi_brazil
        # check for values already calculated
        if not values:
            values = [self.poluents[pol]["aqi_value"] for pol in self.poluents.keys() if "aqi_value" in self.poluents[pol].keys()]
            if len(values) > 0:
                return max(values)
            else: 
                raise """Nenhum valor de poluente pré-calculado ou concentração especificada para o cálculo. 
                Passe os valores das concentrações na variável `values`."""
        # calculate values
        aqis = []
        for pol, value in values.items():
            i = get_iaqi(self, value, pol, algo=None)
            aqis.append(i)
            
        return max(aqis)