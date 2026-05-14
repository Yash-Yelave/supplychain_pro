from abc import ABC, abstractmethod

class RegionStrategy(ABC):
    @property
    @abstractmethod
    def default_currency(self) -> str:
        pass
        
    @abstractmethod
    def calculate_shipping_multiplier(self, base_weight: float) -> float:
        pass
        
    @abstractmethod
    def get_tax_rate(self) -> float:
        pass

class UAERegion(RegionStrategy):
    @property
    def default_currency(self) -> str:
        return "AED"
        
    def calculate_shipping_multiplier(self, base_weight: float) -> float:
        return base_weight * 1.5
        
    def get_tax_rate(self) -> float:
        return 0.05

class ChinaRegion(RegionStrategy):
    @property
    def default_currency(self) -> str:
        return "CNY"
        
    def calculate_shipping_multiplier(self, base_weight: float) -> float:
        return base_weight * 2.0
        
    def get_tax_rate(self) -> float:
        return 0.13

class GlobalRegion(RegionStrategy):
    @property
    def default_currency(self) -> str:
        return "USD"
        
    def calculate_shipping_multiplier(self, base_weight: float) -> float:
        return base_weight * 3.0
        
    def get_tax_rate(self) -> float:
        return 0.0

def get_region_strategy(country_code: str) -> RegionStrategy:
    strategies = {
        "AE": UAERegion,
        "CN": ChinaRegion,
    }
    strategy_class = strategies.get(country_code.upper(), GlobalRegion)
    return strategy_class()
