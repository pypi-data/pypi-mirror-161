from inewave.nwlistop.modelos.cmarg00med import Submercado, CmargsAnos


from cfinterface.files.blockfile import BlockFile
import pandas as pd  # type: ignore
from typing import Type, TypeVar, Optional


class Cmarg00med(BlockFile):
    """
    Armazena os dados das saídas referentes aos custos marginais de
    operação médios entre os patamares.

    Esta classe lida com as informações de saída fornecidas pelo
    NWLISTOP e reproduzidas nos `cmarg00x-med.out`, onde x varia conforme o
    submercado em questão.

    """

    T = TypeVar("T")

    BLOCKS = [
        Submercado,
        CmargsAnos,
    ]

    def __init__(self, data=...) -> None:
        super().__init__(data)
        self.__cmargs = None

    @classmethod
    def le_arquivo(
        cls, diretorio: str, nome_arquivo="cmarg001-med.out"
    ) -> "Cmarg00med":
        return cls.read(diretorio, nome_arquivo)

    def escreve_arquivo(self, diretorio: str, nome_arquivo="cmarg001-med.out"):
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
        for b in self.data.of_type(CmargsAnos):
            dados = b.data
            if dados is None:
                continue
            elif df is None:
                df = b.data
            else:
                df = pd.concat([df, b.data], ignore_index=True)
        return df

    @property
    def custos(self) -> Optional[pd.DataFrame]:
        """
        Tabela com os custos marginai por série e
        por mês/ano de estudo.

        - Ano (`int`)
        - Série (`int`)
        - Janeiro (`float`)
        - ...
        - Dezembro (`float`)

        :return: A tabela dos custos marginais.
        :rtype: pd.DataFrame | None
        """
        if self.__cmargs is None:
            self.__cmargs = self.__monta_tabela()
        return self.__cmargs

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
