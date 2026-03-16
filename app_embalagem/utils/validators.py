def validar_texto_obrigatorio(valor: str, campo: str):
    if not valor or not valor.strip():
        return f"O campo '{campo}' é obrigatório."
    return None


def validar_quantidade(valor: str):
    if not valor.isdigit() or int(valor) <= 0:
        return "Quantidade deve ser um número inteiro maior que zero."
    return None
