#!/usr/bin/env python3
"""
Instalador em Fila para Windows
Instala programas sequencialmente via winget com verificação de versões
"""

import subprocess
import json
import logging
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Package:
    """Definição de um pacote a instalar"""
    name: str                          # Nome legível (ex: "Git")
    winget_id: str                     # ID do winget (ex: "Git.Git")
    version_command: str               # Comando para verificar versão (ex: "git --version")


class WindowsInstallerQueue:
    """Gerenciador de fila de instalação para Windows"""
    
    def __init__(self):
        self.queue: List[Package] = []
        self.results = []
        self.failed_packages = []
    
    def add_package(self, package: Package):
        """Adiciona pacote à fila"""
        self.queue.append(package)
        logger.info(f"📦 Pacote adicionado: {package.name}")
    
    def add_packages(self, packages: List[Package]):
        """Adiciona múltiplos pacotes"""
        for package in packages:
            self.add_package(package)
    
    def is_installed(self, package: Package) -> bool:
        """Verifica se o pacote já está instalado"""
        try:
            result = subprocess.run(
                package.version_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Erro ao verificar {package.name}: {e}")
            return False
    
    def get_version(self, package: Package) -> Optional[str]:
        """Obtém versão instalada"""
        try:
            result = subprocess.run(
                package.version_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Retorna a primeira linha da saída
                return result.stdout.strip().split('\n')[0]
            return None
        except Exception:
            return None
    
    def install_package(self, package: Package) -> bool:
        """Instala um pacote via winget"""
        logger.info(f"⏳ Instalando: {package.name} ({package.winget_id})...")
        
        try:
            result = subprocess.run(
                f"winget install {package.winget_id} -e -h",
                shell=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
            
            if result.returncode == 0:
                version = self.get_version(package)
                logger.info(f"✅ {package.name} instalado com sucesso! (v: {version})")
                self.results.append({
                    'package': package.name,
                    'winget_id': package.winget_id,
                    'status': 'success',
                    'version': version,
                    'timestamp': datetime.now().isoformat()
                })
                return True
            else:
                error_msg = result.stderr or result.stdout or "Erro desconhecido"
                logger.error(f"❌ Erro ao instalar {package.name}: {error_msg}")
                self.failed_packages.append(package.name)
                self.results.append({
                    'package': package.name,
                    'winget_id': package.winget_id,
                    'status': 'failed',
                    'error': error_msg[:200],  # Primeiros 200 caracteres
                    'timestamp': datetime.now().isoformat()
                })
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ Timeout ao instalar {package.name}")
            self.failed_packages.append(package.name)
            self.results.append({
                'package': package.name,
                'winget_id': package.winget_id,
                'status': 'timeout',
                'timestamp': datetime.now().isoformat()
            })
            return False
        except Exception as e:
            logger.error(f"⚠️ Exceção ao instalar {package.name}: {e}")
            self.failed_packages.append(package.name)
            self.results.append({
                'package': package.name,
                'winget_id': package.winget_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return False
    
    def process_queue(self, skip_installed: bool = True):
        """
        Processa a fila de instalação
        
        Args:
            skip_installed: Se True, pula o que já está instalado
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Iniciando instalação de {len(self.queue)} pacotes...")
        logger.info(f"{'='*60}\n")
        
        for i, package in enumerate(self.queue, 1):
            logger.info(f"\n[{i}/{len(self.queue)}] {package.name}")
            logger.info(f"{'-'*60}")
            
            # Verifica se já está instalado
            if skip_installed and self.is_installed(package):
                version = self.get_version(package)
                logger.info(f"⊘ {package.name} já está instalado (v: {version})")
                self.results.append({
                    'package': package.name,
                    'winget_id': package.winget_id,
                    'status': 'skipped',
                    'version': version,
                    'timestamp': datetime.now().isoformat()
                })
                continue
            
            # Instala
            self.install_package(package)
            
        self.print_summary()
    
    def print_summary(self):
        """Exibe resumo da instalação"""
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMO DA INSTALAÇÃO")
        logger.info("="*60)
        
        for result in self.results:
            status_icon = {
                'success': '✅',
                'failed': '❌',
                'skipped': '⊘',
                'timeout': '⏱️',
                'error': '⚠️'
            }.get(result['status'], '?')
            
            version_str = f" (v: {result.get('version', 'N/A')})" if 'version' in result else ""
            logger.info(f"{status_icon} {result['package']}: {result['status']}{version_str}")
        
        logger.info("="*60)
        total = len(self.results)
        success = sum(1 for r in self.results if r['status'] == 'success')
        skipped = sum(1 for r in self.results if r['status'] == 'skipped')
        failed = len(self.failed_packages)
        
        logger.info(f"Total: {total} | ✅ Sucesso: {success} | ⊘ Pulados: {skipped} | ❌ Falhas: {failed}")
        logger.info("="*60 + "\n")
    
    def save_report(self, filepath: str = "installation_report.json"):
        """Salva relatório em JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Relatório salvo em: {filepath}\n")


# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

if __name__ == "__main__":
    # Definir pacotes a instalar
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
            version_command="7z.exe | find /i version"
        ),
    ]
    
    # Executar instalador
    installer = WindowsInstallerQueue()
    installer.add_packages(packages)
    installer.process_queue(skip_installed=True)
    installer.save_report()
