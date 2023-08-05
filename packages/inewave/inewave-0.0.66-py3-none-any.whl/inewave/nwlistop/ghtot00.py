from inewave.nwlistop.modelos.ghtot00 import REE, GHAnos

from cfinterface.files.blockfile import BlockFile
import pandas as pd  # type: ignore
from typing import Type, TypeVar, Optional


class Ghtot00(BlockFile):
    """
    Armazena os dados das saídas referentes à geração hidraulica total
    por patamar, por REE.

    Esta classe lida com as informações de saída fornecidas pelo
    NWLISTOP e reproduzidas nos `ghtot00x.out`, onde x varia conforme o
    REE em questão.

    """

    T = TypeVar("T")

    BLOCKS = [
        REE,
        GHAnos,
    ]

    def __init__(self, data=...) -> None:
        super().__init__(data)
        self.__earms = None

    @classmethod
    def le_arquivo(
        cls, diretorio: str, nome_arquivo="ghtot001.out"
    ) -> "Ghtot00":
        return cls.read(diretorio, nome_arquivo)

    def escreve_arquivo(self, diretorio: str, nome_arquivo="ghtot001.out"):
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
        for b in self.data.of_type(GHAnos):
            dados = b.data
            if dados is None:
                continue
            elif df is None:
                df = b.data
            else:
                df = pd.concat([df, b.data], ignore_index=True)
        return df

    @property
    def geracao(self) -> Optional[pd.DataFrame]:
        """
        Tabela com a geração hidráulica total por série e
        por mês/ano de estudo.

        - Ano (`int`)
        - Série (`int`)
        - Patamar (`str`)
        - Janeiro (`float`)
        - ...
        - Dezembro (`float`)

        :return: A tabela da geração hidráulica.
        :rtype: pd.DataFrame | None
        """
        if self.__earms is None:
            self.__earms = self.__monta_tabela()
        return self.__earms

    @property
    def ree(self) -> Optional[str]:
        """
        O REE associado ao arquivo lido.

        :return: Os nome do REE
        :rtype: str
        """
        b = self.__bloco_por_tipo(REE, 0)
        if b is not None:
            return b.data
        return None
