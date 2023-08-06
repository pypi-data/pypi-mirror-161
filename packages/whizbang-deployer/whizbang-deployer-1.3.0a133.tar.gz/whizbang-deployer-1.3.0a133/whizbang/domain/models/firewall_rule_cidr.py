from typing import Optional

from pydantic import BaseModel


class FirewallRuleCIDR(BaseModel):
    name: str
    cidr_ip_range: str
    type: Optional[str] = None
