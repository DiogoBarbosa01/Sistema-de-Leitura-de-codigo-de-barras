from sqlalchemy import select

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

        if len(senha) < 6:
            raise ValueError("A senha deve ter ao menos 6 caracteres.")

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
        return usuario

    def listar_usuarios(self, session):
        return session.scalars(select(Usuario).order_by(Usuario.nome)).all()
