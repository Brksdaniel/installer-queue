# 🚀 Instalador em Fila para Windows

Instalador automático que instala programas sequencialmente via **winget** com verificação de versões.

## ✨ Características

- ✅ Instalação sequencial (um por vez)
- ✅ Verifica se já está instalado
- ✅ Mostra versão instalada
- ✅ Relatório JSON ao final
- ✅ Timeout de 10 minutos por pacote
- ✅ Emojis para visualizar status

## 🛠️ Requisitos

- Windows 10/11
- Python 3.8+
- `winget` instalado (vem com Windows 11)

## 📦 Instalação

```bash
# Clonar repositório
git clone https://github.com/Brksdaniel/installer-queue.git
cd installer-queue
```

## 🚀 Como Usar

### 1. Customizar os programas

Abra `installer.py` e modifique a lista `packages`:

```python
packages = [
    Package(
        name="Git",
        winget_id="Git.Git",
        version_command="git --version"
    ),
    Package(
        name="Python",
        winget_id="Python.Python.3.11",
        version_command="python --version"
    ),
    # Adicione mais programas aqui
]
```

### 2. Encontrar IDs do winget

```bash
winget search "nome do programa"
```

Exemplo:
```bash
winget search Spotify
```

### 3. Rodar o instalador

```bash
python installer.py
```

## 📄 Saída

O instalador gera um arquivo `installation_report.json` com o resultado de cada instalação:

```json
[
  {
    "package": "Git",
    "winget_id": "Git.Git",
    "status": "success",
    "version": "git version 2.40.0",
    "timestamp": "2026-05-01T10:30:45.123456"
  }
]
```

## 📊 Status Possíveis

- ✅ `success` - Instalado com sucesso
- ⊘ `skipped` - Já estava instalado
- ❌ `failed` - Erro durante instalação
- ⏱️ `timeout` - Instalação demorou muito
- ⚠️ `error` - Exceção durante processo

## 👨‍💻 Autor

Criado por **Brksdaniel**

## 📝 Licença

MIT