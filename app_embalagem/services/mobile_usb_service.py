import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class MobileUsbStatus:
    conectado: bool
    mensagem: str


class MobileUsbService:
    """
    Integração opcional via ADB para leitura de código vindo do celular em USB.

    Fluxo esperado no celular (app externo):
    - Escrever o último código lido em /sdcard/embalagem_scan_code.txt
    - Opcionalmente limpar o arquivo após consumo.
    """

    DEVICE_SCAN_FILE = "/sdcard/embalagem_scan_code.txt"

    def __init__(self):
        self._ultimo_codigo = ""

    @staticmethod
    def _adb_disponivel() -> bool:
        return shutil.which("adb") is not None

    def status_conexao(self) -> MobileUsbStatus:
        if not self._adb_disponivel():
            return MobileUsbStatus(False, "ADB não encontrado no sistema.")

        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=2)
        except Exception:
            return MobileUsbStatus(False, "Falha ao verificar dispositivos ADB.")

        linhas = [l.strip() for l in result.stdout.splitlines() if l.strip()]
        conectados = [l for l in linhas[1:] if l.endswith("\tdevice")]
        if conectados:
            serial = conectados[0].split("\t")[0]
            return MobileUsbStatus(True, f"Celular USB detectado: {serial}")
        return MobileUsbStatus(False, "Nenhum celular USB detectado.")

    def ler_codigo_usb(self) -> str | None:
        status = self.status_conexao()
        if not status.conectado:
            return None

        try:
            result = subprocess.run(
                ["adb", "shell", "cat", self.DEVICE_SCAN_FILE],
                capture_output=True,
                text=True,
                timeout=2,
            )
        except Exception:
            return None

        if result.returncode != 0:
            return None

        codigo = (result.stdout or "").strip().upper()
        if not codigo or codigo == self._ultimo_codigo:
            return None

        self._ultimo_codigo = codigo
        return codigo
