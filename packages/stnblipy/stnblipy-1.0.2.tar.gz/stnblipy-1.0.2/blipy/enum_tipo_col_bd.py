
"""
Enumeradores para tipos de colunas no banco de dados. 
"""

from enum import Enum, auto

# TODO: criar demais tipos possíveis do banco (como bool)

# Tipos de colunas no banco de dados
class TpColBD(Enum):
    STRING  = auto()
    INT     = auto()
    NUMBER  = auto()
    DATE    = auto()
    BOOL    = auto()

