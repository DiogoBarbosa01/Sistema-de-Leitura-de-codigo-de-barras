# Sistema de Controle de Embalagem (Desktop)

Aplicativo desktop em **Python + PySide6** para:
- cadastrar funcionários.
- cadastrar caixas.
- gerar código de barras Code 128 para melhor filtro e registro.
- ler códigos via scanner USB (como teclado).
- registrar leituras também por celular via Binare Eye(futuramente vamos criar um app de scam original).
- rastrear produtividade e histórico.
- 
(alguns commits foi usado a ferramenta codex para otimização de codigo)
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
- PySide 6
- windows 10 +
- Binare Eye
- Força de Vontade

## 2) Criar banco PostgreSQL (todos sabem ne)

```sql
CREATE DATABASE app_embalagem;
CREATE USER embalagem_user WITH PASSWORD '...';
GRANT ALL PRIVILEGES ON DATABASE embalagem_db TO embalagem_user;
```
(USE O SQL SHELL PARA CRIAR O DB, MUITO MAIS FÁCIL E PRÁTICO)

## EXTRAS DO TOPICO 2
- Dbeaver ou PgAdmin 4 para monitorar as tabelas em tempo real.(eu prefiro o dbeaver)
- Lembre de criar a porta no sistema meu amigo, ele não tem bola de cristal para linkar automático. 
- Caso esteja sendo seu inicio com o DataBase do sistema e quer mudar uma tabela e ta com preguiça de atualizar o DB devida a alta etapa pior que o site do GOV?

No SQL SHELL
```
\c nome do db
#nome do db:DROP SCHEMA public CASCADE;          
#nome do db:CREATE SCHEMA public;`
```
- Voce apagou as tabelas antigas e recriou elas do zero agora atualizadas, **lembre sempre de fazer alterações na tabela dessa forma quando ainda não for o sistema original** que está no ar, rapido e prático.

- caso faça isso e deseja que as tabelas sejam recriadas, só abrir seu app e elas criam novamente do zero.

## 3) Configurar ambiente

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r app_embalagem/requirements.txt
```
- Caso fique na duvida se a venv esta correta, ele aparece escrito (venv) mas se to for bobado e seu terminal não apareceu, so dar um `ls`

## 4) Configurar conexão
Use variáveis de ambiente (opcional). Se não definir, usa defaults do `config.py`.

```bash
export DB_HOST=localhost
export DB_PORT=****
export DB_NAME=app_embalagem
export DB_USER=user
export DB_PASSWORD=...
```

Ou defina `DATABASE_URL` diretamente:

```bash
export DATABASE_URL='postgresql+psycopg2://embalagem_user:embalagem123@localhost:****/app_embalagem'
```

## 5) Inicializar banco e rodar app

```bash
python -m app_embalagem.database.init_db
python -m app_embalagem.main(recomendo mais esse)
```

### Login padrão
- usuário: `...`
- senha: `...`

## 6) Fluxo do scanner
1. Escaneie o codigo de barras no padrão `CX-AADDMSSMMMMUUUUUU` colado na caixa para filtrar suas informações de forma rápida.
2. O Scanneamento funciona automaticamente quando o sistema liga, desde que tenha:
3. Um celular conectado ou um scanner capaz de ler Code 128.

## 7) Leitura por celular
A tela do scanner possui campo **Leitura por celular**.
- Use app de leituras com configuração de encaminhamento de URL no celular para obter o valor do código.
- Tenho o ADB instalado e configurado
- Esteja linkado com um USB e na mesma Rede Wifi.

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
- O cadastro de usuário fica disponível na tela de login (botão **Cadastrar usuário**), com seleção de perfil `admin` ou `operador`.
- **admin** abre a `PageAdmin` com acesso a cadastro de funcionário, Cadastro de caixa, Busca De Caixa, Dashboard, Codigo de barras.
- **operador** abre a `PageOperador` com acesso a: Cadastro de caixa, Busca De Caixa, Dashboard, Codigo de barras.
- 


## 10) Regras da etiqueta de caixa
- Campos da caixa: **Nº do pedido** (4 dígitos), **Artigo**, **Cor**, **Emendas** e **Metros** (metros de fita na caixa).
- Ao clicar em **Gerar etiqueta**, o sistema já salva a caixa e gera o barcode em uma única ação.
- O código da caixa segue o padrão: `CX-AADDMSSMMMMUUUUUU`
  - `AA`: ano (2 dígitos)
  - `DD`: dia (2 dígitos)
  - `M`: mês em letra (`A` janeiro ... `L` dezembro)
  - `SS`: 2 primeiras letras do funcionário
  - `MMMM`: matrícula (4 dígitos, com zero à esquerda se necessário)
  - `UUUUUU`: identificador único interno sequencial
- Após gerar, a tela mostra pré-visualização da etiqueta e botão **Imprimir**.

## 11) Leitura automática por celular USB (ADB)
- A tela de scanner agora monitora celular conectado por USB usando **ADB** (Android Debug Bridge)
- Esse App ajuda o sistema fazer uma varredura no aparelho criando uma conexão Pc -> celular via depuração USB, ele também pode ser usado via WIFI se for bem configurado.
- Quando um código novo é detectado via USB, o sistema processa automaticamente e abre uma janela com os dados da caixa.
- Link da Pagina Oficial para quem quiser dar uma estudada e entender mais essa API(muito boa inclusive) https://developer.android.com/tools/adb?hl=pt-br
 
- Pré-requisitos:
  1. `adb` instalado no PC
  2. depuração USB habilitada no Android(Precisa do modo desenvolvedor do celular ativo para habilitar)
  3. Ativa o adb no projeto via bash(`adb start server`).
  4. Verificar se o celular está sendo reconhecido(`adb device`) no Bash
  5. Se aparecer `unauthorized`, reconecte o cabo e aceite o aviso no celular.
  6. app de escaneamento de codigo precisa ter funcionalidade de encaminhamento via URL e como modo de conexão POST/JSON ou GET Completo.
- O monitor não bloqueia o sistema: se o ADB não estiver disponível, o scanner manual continua funcionando normalmente.


### 11.1) Envio de solicitação de busca pelo celular (Binary Eye e similares)
Além do modo ADB, o Scanner abre um endpoint HTTP local para receber códigos do celular em tempo real.

> Sim, a URL pode (e deve) ser o **IP do PC** na rede local.

Opções aceitas:
- `GET http://IP_DO_PC:8765/scan?code=CX-...`
- `POST http://IP_DO_PC:8765/scan` com JSON `{"code":"CX-..."}`
- `POST/GET` também aceita campos alternativos: `codigo`, `text`, `data`, `scan`, `value`.

Fluxo no sistema:
1. Chega solicitação do celular.
2. O sistema exibe popup: **"Leitura de código a ser realizada"** com botões **Confirmar/Cancelar**.
3. Ao confirmar, abre a Janela de dados da caixa (incluindo artigo, cor, emendas e nome completo do funcionário).

Configuração sugerida no Binary Eye (IP do PC: `192.168.2.110`):
- Ativar "Encaminhar digitalizações".

**Se o tipo for `POST application/json`:**
- URL de encaminhamento: `http://192.168.2.110:876/scan`
- Body JSON: `{"code":"{CODE}"}`

**Se o tipo for `POST application/x-www-form-urlencoded`:**
- URL de encaminhamento: `http://192.168.2.110:8765/scan`
- Body (form): `code={CODE}`

**Se o tipo for `GET`:**
- URL de encaminhamento: `http://192.168.2.110:8765/scan?code={CODE}`

Observações:
- `{CODE}` representa o texto lido pelo scanner (o nome do placeholder pode variar no app).
- Deixe celular e PC na mesma rede local.

## 12) Configurações USB obrigatórias no celular (Android)
Para o celular ser reconhecido no sistema via USB/ADB:
1. Ative **Opções do desenvolvedor** no Android.(clica 7x no numero de versão do celular)
2. Ative **Depuração USB**.
3. Ao conectar no PC, selecione modo USB **Transferência de arquivos** (evite somente carregamento).
4. Aceite o pop-up **Permitir depuração USB** no celular (marque “Sempre permitir”).



## 13) Aplicativos compatíveis para leitura de código
O sistema aceita qualquer app de scanner no celular que consiga entregar o texto lido para o arquivo:
`/sdcard/embalagem_scan_code.txt`

Exemplos de apps que podem ser usados no Android (com automação/atalho para salvar texto):
- **Barcode Scanner** (ZXing)
- **QR & Barcode Scanner** (Gamma Play)
- **Binary Eye**(acho o mais fácil)
- **Scandit Keyboard Wedge** (cenário corporativo)

> Observação: o app precisa exportar o valor lido para arquivo (ou integração equivalente), pois o monitor USB lê desse caminho via ADB.

## 14) Organização dos códigos de barras
- Foi adicionada a aba **Códigos de Barras** no sistema.
- Estrutura de arquivos:
  - `assets/barcodes/<numero_pedido>/`
  - dentro de cada pasta ficam os PNGs gerados para aquele número de pedido.

## 15) Configuração USB no PC (guia dedicado)
- Veja o arquivo `README_USB_PC.md` para instruções completas de Windows/Linux/macOS e diagnóstico ADB.

## 16) PIP INSTALL
 - Todos os PIP install necessários.
  
 ```Bash
- pip install pyside
- pip install sqlalchemy
- pip install psycopg2-binary
- pip install python-barcode
- pip install pillow
- pip install pyinstaller
- pip install pyside6
  ```

Use eles caso necessite abrir o sistema em outros computadores para edição de codigo
