# Video Analyzer com Google Cloud & Gemini

Este é um projeto em Python para análise automática de vídeos, gerando um arquivo `.txt` com timestamps, transcrição de áudio (via Faster Whisper) e descrição visual detalhada (via Gemini 2.0 Flash).  
Indicado para sumarização multimodal de vídeos de reuniões, aulas, entrevistas e outros contextos.

## Pré-requisitos

- Conta Google Cloud com acesso ao modelo Gemini 2.0 Flash (ou similar)
- Chave de conta de serviço (formato JSON)
- Python 3.8 ou superior
- ffmpeg instalado no sistema  
  - Linux: `sudo apt install ffmpeg`  
  - macOS: `brew install ffmpeg`
- Dependências Python listadas em `requirements.txt`

## Instalação

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuração

### Chave de serviço

Coloque o arquivo JSON da sua Service Account em:

```
credentials/key.json
```

### Vídeos

Adicione os arquivos de vídeo na pasta:

```
videos/
```

Exemplo: `videos/video1biomundo.mp4`

### Script principal

Edite o `main.py` para definir o caminho do vídeo e o nome do arquivo de saída conforme necessário.

## Execução

```bash
python main.py
```

O resultado será salvo como `video1biomundo_resultado.txt` (ou nome equivalente) na raiz do projeto.

## Estrutura de Pastas

```
ANALYZER/
├── credentials/
│   └── key.json
├── venv/
├── videos/
│   └── video1biomundo.mp4
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
└── video1biomundo_resultado.txt
```

## Observações

- O tempo de execução pode variar conforme a quota disponível na API Gemini.
- O parâmetro `interval`, no `main.py`, define a frequência da análise visual (em segundos).
- A transcrição de áudio é feita localmente com Faster Whisper, sem limitação de tamanho.
- Arquivos de credenciais e saídas `.txt` estão no `.gitignore` por segurança.
- Para processar outro vídeo, basta alterar o caminho configurado no script.

## Tecnologias

- Python
- Google Cloud (Gemini 2.0 Flash)
- Faster Whisper
- ffmpeg