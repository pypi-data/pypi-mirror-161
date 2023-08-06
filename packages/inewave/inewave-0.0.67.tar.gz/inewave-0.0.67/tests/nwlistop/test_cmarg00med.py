from inewave.nwlistop.cmarg00med import Cmarg00med

from tests.mocks.mock_open import mock_open
from unittest.mock import MagicMock, patch

from tests.mocks.arquivos.cmarg00med import MockCmarg00Med


def test_atributos_encontrados_cmarg00med():
    m: MagicMock = mock_open(read_data="".join(MockCmarg00Med))
    with patch("builtins.open", m):
        n = Cmarg00med.le_arquivo("")
        assert n.custos is not None
        assert n.custos.iloc[0, 0] == 2021
        assert n.custos.iloc[-1, -1] == 354.22
        assert n.submercado is not None
        assert n.submercado == "SUDESTE"


def test_atributos_nao_encontrados_cmarg00med():
    m: MagicMock = mock_open(read_data="")
    with patch("builtins.open", m):
        n = Cmarg00med.le_arquivo("")
        assert n.custos is None
        assert n.submercado is None


def test_eq_cmarg00med():
    m: MagicMock = mock_open(read_data="".join(MockCmarg00Med))
    with patch("builtins.open", m):
        n1 = Cmarg00med.le_arquivo("")
        n2 = Cmarg00med.le_arquivo("")
        assert n1 == n2


# Não deve ter teste de diferença, visto que o atributo é
# implementado como Lazy Property.
