import re


def validar_texto_obrigatorio(valor: str, campo: str):
    if not valor or not valor.strip():
        return f"O campo '{campo}' é obrigatório."
    return None


def validar_metros(valor: str):
    try:
        metros = float(valor.replace(",", "."))
    except ValueError:
        return "Metros deve ser um número válido (ex.: 150.5)."

    if metros <= 0:
        return "Metros deve ser maior que zero."
    return None


def validar_numero_pedido(valor: str):
    if not re.fullmatch(r"\d{4}", valor.strip()):
        return "Nº do pedido deve conter exatamente 4 números."
    return None
