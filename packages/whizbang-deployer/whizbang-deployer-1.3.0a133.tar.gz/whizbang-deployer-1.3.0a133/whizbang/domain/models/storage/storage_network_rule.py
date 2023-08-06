from whizbang.domain.models.firewall_rule_cidr import FirewallRuleCIDR
from typing import Optional

from pydantic import BaseModel


class StorageNetworkRuleBase(BaseModel):
    resource_group_name: str
    storage_account_name: str


class StorageIPNetworkRule(StorageNetworkRuleBase):
    firewall_rule_cidr: FirewallRuleCIDR


class StorageVnetIPNetworkRule(StorageNetworkRuleBase):
    vnet_name: Optional[str]
    subnet: str
