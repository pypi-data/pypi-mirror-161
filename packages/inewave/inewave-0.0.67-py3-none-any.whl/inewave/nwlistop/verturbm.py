from inewave.nwlistop.modelos.verturbm import Submercado, VertAnos

from cfinterface.files.blockfile import BlockFile
import pandas as pd  # type: ignore
from typing import Type, TypeVar, Optional


class Verturbm(BlockFile):
    """
    Armazena os dados das saídas referentes às energias
    vertidas, por submercado.

    Esta classe lida com as informações de saída fornecidas pelo
    NWLISTOP e reproduzidas nos `vertub00x.out`, onde x varia conforme o
    REE em questão.

    """

    T = TypeVar("T")

    BLOCKS = [
        Submercado,
        VertAnos,
    ]

    def __init__(self, data=...) -> None:
        super().__init__(data)
        self.__earms = None

    @classmethod
    def le_arquivo(
        cls, diretorio: str, nome_arquivo="verturbm001.out"
    ) -> "Verturbm":
        return cls.read(diretorio, nome_arquivo)

    def escreve_arquivo(self, diretorio: str, nome_arquivo="verturbm001.out"):
        self.write(diretorio, nome_arquivo)

    def __bloco_por_tipo(self, bloco: Type[T], indice: int) -> Optional[T]:
        """
        Obtém um gerador de blocos de um tipo, se houver algum no arquivo.

        :param bloco: Um tipo de bloco para ser lido
        :type bloco: T
        :param indice: O índice do bloco a ser acessado, dentre os do tipo
        :type indice: int
        :return: O gerador de blocos, se houver
        :rtype: Optional[Generator[T], None, None]
        """
        try:
            return next(
                b
                for i, b in enumerate(self.data.of_type(bloco))
                if i == indice
            )
        except StopIteration:
            return None

    def __monta_tabela(self) -> pd.DataFrame:
        df = None
        for b in self.data.of_type(VertAnos):
            dados = b.data
            if dados is None:
                continue
            elif df is None:
                df = b.data
            else:
                df = pd.concat([df, b.data], ignore_index=True)
        return df

    @property
    def vertimentos(self) -> Optional[pd.DataFrame]:
        """
        Tabela com as energias vertidas por série e
        por mês/ano de estudo.

        - Ano (`int`)
        - Série (`int`)
        - Janeiro (`float`)
        - ...
        - Dezembro (`float`)

        :return: A tabela das energias vertidas.
        :rtype: pd.DataFrame
        """
        if self.__earms is None:
            self.__earms = self.__monta_tabela()
        return self.__earms

    @property
    def submercado(self) -> Optional[str]:
        """
        O submercado associado ao arquivo lido.

        :return: Os nome do submercado
        :rtype: str
        """
        b = self.__bloco_por_tipo(Submercado, 0)
        if b is not None:
            return b.data
        return None
