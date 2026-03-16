from datetime import datetime


def formatar_data_hora(valor: datetime | None) -> str:
    if not valor:
        return "-"
    return valor.strftime("%d/%m/%Y %H:%M:%S")
