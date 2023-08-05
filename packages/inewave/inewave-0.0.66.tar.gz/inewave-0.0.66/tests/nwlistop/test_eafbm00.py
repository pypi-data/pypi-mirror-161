from inewave.nwlistop.eafbm00 import Eafbm00

from tests.mocks.mock_open import mock_open
from unittest.mock import MagicMock, patch

from tests.mocks.arquivos.eafbm00 import MockEafbm00


def test_atributos_encontrados_eafbm00():
    m: MagicMock = mock_open(read_data="".join(MockEafbm00))
    with patch("builtins.open", m):
        n = Eafbm00.le_arquivo("")
        assert n.energias is not None
        assert n.energias.iloc[0, 0] == 1995
        assert n.energias.iloc[-1, -1] == 38424.0
        assert n.submercado is not None
        assert n.submercado == "SUDESTE"


def test_atributos_nao_encontrados_eafbm00():
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        n = Eafbm00.le_arquivo("")
        assert n.energias is None
        assert n.submercado is None


def test_eq_eafbm00():
    m: MagicMock = mock_open(read_data="".join(MockEafbm00))
    with patch("builtins.open", m):
        n1 = Eafbm00.le_arquivo("")
        n2 = Eafbm00.le_arquivo("")
        assert n1 == n2


# Não deve ter teste de diferença, visto que o atributo é
# implementado como Lazy Property.
