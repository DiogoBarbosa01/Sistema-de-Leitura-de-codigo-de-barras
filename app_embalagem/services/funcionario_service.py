from sqlalchemy import func, select

from app_embalagem.models.funcionario import Funcionario


class FuncionarioService:
    @staticmethod
    def _gerar_proximo_codigo(session) -> str:
        total = session.scalar(select(func.count(Funcionario.id))) or 0
        return f"FUNC-{total + 1:04d}"

    def criar_funcionario(self, session, nome: str, matricula: str, ativo: bool = True) -> Funcionario:
        codigo = self._gerar_proximo_codigo(session)
        funcionario = Funcionario(nome=nome, matricula=matricula, codigo_barras=codigo, ativo=ativo)
        session.add(funcionario)
        session.commit()
        session.refresh(funcionario)
        return funcionario

    def buscar_por_codigo(self, session, codigo: str) -> Funcionario | None:
        return session.scalar(select(Funcionario).where(Funcionario.codigo_barras == codigo))

    def listar_todos(self, session):
        return session.scalars(select(Funcionario).order_by(Funcionario.nome)).all()
