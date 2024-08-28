# Auto Watermark desktop

O Auto Watermark é um projeto Python que aaplica marcas d'água em vídeos e os renderiza.

## Pré-requisitos

Certifique-se de ter:
 Python instalado em sua máquina. Você pode baixar e instalar Python em [python.org](https://www.python.org/) ou em [pyenv](https://github.com/pyenv/pyenv) (recomendado).

 Git instalado.

 FFMPEG instalado.

## Preparando o ambiente do projeto

Para preparar o ambiente do projeto, siga estas etapas:

1. **Crie a venv:**
   Use o comando para criar a venv sempre que instalar o projeto pela primeira vez

   terminal git bash:
   python3 -m venv venv

2. **Ative a venv:**
   Use o comando para ativar a venv sempre que entrar no projeto

   terminal git bash:
   source venv/Scripts/activate

3. **Instale as dependências:**
   Use o comando pip para instalar todas as dependências necessárias listadas no arquivo requirements.txt.

   terminal git bash:
   pip install -r requirements.txt

4. **Rode o projeto:**
   Para inicializar o projeto e aplicar a marca d'água nos vídeos, execute o seguinte comando:

   terminal git bash:
   python auto_watermark.py