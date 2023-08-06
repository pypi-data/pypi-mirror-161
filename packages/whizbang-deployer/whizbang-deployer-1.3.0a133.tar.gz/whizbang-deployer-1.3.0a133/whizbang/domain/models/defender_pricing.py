from pydantic import BaseModel

class DefenderPricing(BaseModel):
    id: str
    name: str    
    pricing_tier: str
    
    @property
    def type_(self) -> str:
        return "Microsoft.Security/pricings"