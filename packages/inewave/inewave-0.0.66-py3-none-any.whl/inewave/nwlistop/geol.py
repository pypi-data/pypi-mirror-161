from inewave.nwlistop.modelos.geol import PEE, GEAnos

from cfinterface.files.blockfile import BlockFile
import pandas as pd  # type: ignore
from typing import Type, TypeVar, Optional


class Geol(BlockFile):
    """
    Armazena os dados das saídas referentes à geração eólica total
    por patamar, por PEE.

    Esta classe lida com as informações de saída fornecidas pelo
    NWLISTOP e reproduzidas nos `geol00x.out`, onde x varia conforme o
    PEE em questão.

    """

    T = TypeVar("T")

    BLOCKS = [
        PEE,
        GEAnos,
    ]

    def __init__(self, data=...) -> None:
        super().__init__(data)
        self.__geracao = None

    @classmethod
    def le_arquivo(cls, diretorio: str, nome_arquivo="geol001.out") -> "Geol":
        return cls.read(diretorio, nome_arquivo)

    def escreve_arquivo(self, diretorio: str, nome_arquivo="geol001.out"):
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
        for b in self.data.of_type(GEAnos):
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
        Tabela com a geração eólica total por série e
        por mês/ano de estudo.

        - Ano (`int`)
        - Série (`int`)
        - Patamar (`str`)
        - Janeiro (`float`)
        - ...
        - Dezembro (`float`)

        :return: A tabela da geração eólica.
        :rtype: pd.DataFrame
        """
        if self.__geracao is None:
            self.__geracao = self.__monta_tabela()
        return self.__geracao

    @property
    def pee(self) -> Optional[str]:
        """
        O PEE associado ao arquivo lido.

        :return: O nome do PEE
        :rtype: str
        """
        b = self.__bloco_por_tipo(PEE, 0)
        if b is not None:
            return b.data
        return None
