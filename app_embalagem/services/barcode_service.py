from pathlib import Path

import barcode
from barcode.writer import ImageWriter

from app_embalagem.config import BARCODES_DIR


class BarcodeService:
    @staticmethod
    def gerar_codigo_barras(codigo: str, numero_pedido: str | None = None) -> str:
        pasta = Path(BARCODES_DIR)
        if numero_pedido:
            pasta = pasta / str(numero_pedido)
            pasta.mkdir(parents=True, exist_ok=True)

        caminho_base = pasta / codigo
        code128 = barcode.get("code128", codigo, writer=ImageWriter())
        caminho_arquivo = code128.save(str(caminho_base), options={"write_text": True})
        return caminho_arquivo
