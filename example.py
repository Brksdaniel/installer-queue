#!/usr/bin/env python3
"""
Exemplo de uso do Instalador para Windows
Customize com seus programas preferidos
"""

from installer import WindowsInstallerQueue, Package


def main():
    # Criar instância do instalador
    installer = WindowsInstallerQueue()
    
    # Definir seus programas
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
        Package(
            name="Node.js",
            winget_id="OpenJS.NodeJS",
            version_command="node --version"
        ),
        Package(
            name="VSCode",
            winget_id="Microsoft.VisualStudioCode",
            version_command="code --version"
        ),
        Package(
            name="7-Zip",
            winget_id="7zip.7zip",
            version_command="7z.exe"
        ),
    ]
    
    # Adicionar à fila
    installer.add_packages(packages)
    
    # Processar (pula os já instalados)
    installer.process_queue(skip_installed=True)
    
    # Salvar relatório
    installer.save_report("installation_report.json")
    
    print("\n✅ Instalação concluída! Veja o relatório em 'installation_report.json'")


if __name__ == "__main__":
    main()