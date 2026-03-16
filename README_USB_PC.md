# Configuração USB no PC para reconhecer celular (ADB)

Este guia é para fazer a integração **Scanner USB + Celular** funcionar no sistema.

## 1) Instalar Android Platform Tools (ADB)
- Baixe e instale **Android Platform Tools** (contém o `adb`).
- Garanta que o comando funcione no terminal:

```bash
adb version
```

## 2) Configuração no Windows
1. Instale o driver USB do fabricante do celular (Samsung/Xiaomi/Motorola etc.) ou driver Google USB.
2. No **Gerenciador de Dispositivos**, confirme que o aparelho não está com alerta amarelo.
3. Use cabo de dados (não apenas carga).
4. Execute:

```bash
adb kill-server
adb start-server
adb devices
```

5. Deve aparecer `device` (não `unauthorized`/`offline`).

## 3) Configuração no Linux
1. Instale regras **udev** para Android.
2. Reinicie o udev:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

3. Teste:

```bash
adb devices
```

## 4) Configuração no macOS
1. Instale platform-tools (ex.: Homebrew).
2. Teste:

```bash
adb devices
```

## 5) Checklist de diagnóstico rápido
- `adb devices` lista o aparelho como `device`.
- Se aparecer `unauthorized`, desbloqueie o celular e aceite “Permitir depuração USB”.
- Se aparecer vazio, troque cabo/porta USB e use modo **Transferência de arquivos (MTP)**.
- Reinicie ADB:

```bash
adb kill-server && adb start-server && adb devices
```

## 6) Integração esperada com o app
O sistema lê o arquivo:

`/sdcard/embalagem_scan_code.txt`

Um app no celular deve gravar o último código lido nesse arquivo para o sistema detectar automaticamente.
