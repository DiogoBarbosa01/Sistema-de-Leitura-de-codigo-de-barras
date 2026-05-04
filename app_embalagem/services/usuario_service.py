from sqlalchemy import select

from app_embalagem.models.funcionario import Funcionario
from app_embalagem.models.usuario import Usuario
from app_embalagem.services.auth_service import AuthService


class UsuarioService:
    def __init__(self):
        self.auth_service = AuthService()

    def criar_usuario(self, session, username: str, senha: str, nome: str, perfil: str, ativo: bool = True) -> Usuario:
        username = username.strip().lower()
        nome = nome.strip()
        perfil = perfil.strip().lower()

        existente = session.scalar(select(Usuario).where(Usuario.username == username))
        if existente:
            raise ValueError("Já existe um usuário com esse username.")

        if perfil not in {"admin", "operador"}:
            raise ValueError("Perfil inválido. Use admin ou operador.")

        if len(senha) < 4:
            raise ValueError("A senha deve ter ao menos 4 caracteres.")

        usuario = Usuario(
            username=username,
            senha_hash=self.auth_service.gerar_hash_senha(senha),
            nome=nome,
            perfil=perfil,
            ativo=ativo,
        )
        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        if perfil == "operador":
            matricula_operador = username.upper()
            funcionario_existente = session.scalar(select(Funcionario).where(Funcionario.matricula == matricula_operador))
            if not funcionario_existente:
                codigo_base = f"FUNC-OP-{username.upper()}"
                codigo = codigo_base
                sufixo = 1
                while session.scalar(select(Funcionario).where(Funcionario.codigo_barras == codigo)):
                    codigo = f"{codigo_base}-{sufixo}"
                    sufixo += 1

                funcionario = Funcionario(
                    nome=nome,
                    matricula=matricula_operador,
                    codigo_barras=codigo,
                    ativo=ativo,
                )
                session.add(funcionario)
                session.commit()

        return usuario

    def listar_usuarios(self, session):
        return session.scalars(select(Usuario).order_by(Usuario.nome)).all()
