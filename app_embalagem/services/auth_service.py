import hashlib
import hmac
import os

from sqlalchemy import select

from app_embalagem.models.usuario import Usuario


class AuthService:
    @staticmethod
    def gerar_hash_senha(senha: str) -> str:
        salt = os.urandom(16)
        chave = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, 120000)
        return f"{salt.hex()}:{chave.hex()}"

    @staticmethod
    def validar_senha(senha: str, senha_hash: str) -> bool:
        # Suporta o formato atual (salt:hash) e também registros antigos
        # que podem ter sido salvos em texto puro.
        if ":" not in senha_hash:
            return hmac.compare_digest(senha, senha_hash)

        try:
            salt_hex, hash_hex = senha_hash.split(":", maxsplit=1)
            teste = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(salt_hex), 120000)
            return hmac.compare_digest(teste.hex(), hash_hex)
        except (ValueError, TypeError):
            return False

    def autenticar(self, session, username: str, senha: str) -> Usuario | None:
        username = username.strip().lower()
        usuario = session.scalar(select(Usuario).where(Usuario.username == username))
        if not usuario or not usuario.ativo:
            return None
        if not self.validar_senha(senha, usuario.senha_hash):
            return None
        return usuario

    def criar_usuario_inicial(self, session):
        existe = session.scalar(select(Usuario).limit(1))
        if existe:
            return
        usuario = Usuario(
            username="admin",
            senha_hash=self.gerar_hash_senha("admin123"),
            nome="Administrador",
            perfil="admin",
            ativo=True,
        )
        session.add(usuario)
        session.commit()
