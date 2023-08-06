from dataclasses import dataclass


@dataclass
class Config:
    package_name: str = 'client'
    client_name: str = 'Client'
