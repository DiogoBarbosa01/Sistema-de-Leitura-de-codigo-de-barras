from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.services.funcionario_service import FuncionarioService
from app_embalagem.services.movimentacao_service import MovimentacaoService


class ScanService:
    def __init__(self):
        self.funcionario_service = FuncionarioService()
        self.caixa_service = CaixaService()
        self.mov_service = MovimentacaoService()

    def processar_scan(self, session, codigo: str, funcionario_atual=None, origem: str = "usb"):
        codigo = codigo.strip().upper()
        if codigo.startswith("FUNC-"):
            funcionario = self.funcionario_service.buscar_por_codigo(session, codigo)
            if not funcionario or not funcionario.ativo:
                return {"ok": False, "mensagem": "Funcionário inválido ou inativo."}
            return {"ok": True, "tipo": "funcionario", "funcionario": funcionario, "mensagem": f"Funcionário ativo: {funcionario.nome}"}

        if codigo.startswith("CX-"):
            if not funcionario_atual:
                return {"ok": False, "mensagem": "Escaneie primeiro um funcionário ativo."}
            caixa = self.caixa_service.buscar_por_codigo(session, codigo)
            if not caixa:
                return {"ok": False, "mensagem": "Caixa não encontrada."}
            self.caixa_service.atualizar_status(session, caixa, CaixaService.STATUS_EMBALADA)
            self.mov_service.registrar(
                session,
                caixa_id=caixa.id,
                funcionario_id=funcionario_atual.id,
                acao="finalizou_embalagem",
                observacao=f"Leitura via {origem}",
            )
            return {"ok": True, "tipo": "caixa", "caixa": caixa, "mensagem": f"Caixa {caixa.codigo_caixa} embalada com sucesso."}

        return {"ok": False, "mensagem": "Código inválido. Use FUNC-xxxx ou CX-xxxxxx."}

    def processar_scan_celular(self, session, codigo: str, funcionario_atual=None):
        return self.processar_scan(session, codigo, funcionario_atual=funcionario_atual, origem="celular")
