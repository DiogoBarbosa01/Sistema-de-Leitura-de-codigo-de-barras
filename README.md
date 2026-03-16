# Sistema de Controle de Embalagem (Desktop)

Aplicativo desktop em **Python + PySide6** para:
- cadastrar funcionários
- cadastrar caixas
- gerar código de barras Code128
- ler códigos via scanner USB (como teclado)
- registrar leituras também por celular (entrada manual do código lido no app mobile)
- rastrear produtividade e histórico

## Estrutura

```text
app_embalagem/
├── main.py
├── config.py
├── requirements.txt
├── database/
├── models/
├── services/
├── views/
├── utils/
└── assets/barcodes/
```

## 1) Pré-requisitos
- Python 3.11+
- PostgreSQL 13+

## 2) Criar banco PostgreSQL

```sql
CREATE DATABASE embalagem_db;
CREATE USER embalagem_user WITH PASSWORD 'embalagem123';
GRANT ALL PRIVILEGES ON DATABASE embalagem_db TO embalagem_user;
```

## 3) Configurar ambiente

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r app_embalagem/requirements.txt
```

## 4) Configurar conexão
Use variáveis de ambiente (opcional). Se não definir, usa defaults do `config.py`.

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=embalagem_db
export DB_USER=embalagem_user
export DB_PASSWORD=embalagem123
```

Ou defina `DATABASE_URL` diretamente:

```bash
export DATABASE_URL='postgresql+psycopg2://embalagem_user:embalagem123@localhost:5432/embalagem_db'
```

## 5) Inicializar banco e rodar app

```bash
python -m app_embalagem.database.init_db
python -m app_embalagem.main
```

### Login padrão
- usuário: `admin`
- senha: `admin123`

## 6) Fluxo do scanner
1. Escaneie `FUNC-xxxx` para selecionar funcionário ativo.
2. Escaneie `CX-xxxxxx` para finalizar embalagem da caixa.
3. O campo do scanner mantém foco automaticamente.

## 7) Leitura por celular
A tela do scanner possui campo **Leitura por celular**.
- Use qualquer app de leitura no celular para obter o valor do código.
- Cole/digite no campo e clique em **Registrar leitura de celular**.
- O sistema registra a origem como `celular` no histórico.

## 8) Gerar executável com PyInstaller

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --name ControleEmbalagem app_embalagem/main.py
```

O executável ficará em `dist/ControleEmbalagem`.

## Observações
- Etiquetas de código de barras são salvas em `app_embalagem/assets/barcodes/`.
- Arquitetura em camadas pronta para expansão (novos serviços, telas e integrações).


## 9) Perfis e telas iniciais separadas
- **admin** abre a `PageAdmin` com acesso a:
  - cadastro de usuário (com perfil `admin` ou `operador`)
  - cadastro de funcionário
  - cadastro de caixa
  - scanner, dashboard e histórico
- **operador** abre a `PageOperador` com acesso a:
  - scanner, dashboard e histórico

