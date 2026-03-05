# Configuração do ambiente

### Configuração do WSL 2
> wsl --update
> wsl --set-default-version 2
> Instala a versão do ubuntu por padrão
> wsl --install
> wsl -l -v

### Habilitar a integração do wsl
* Docker Desktop
* Clique no ícone de Engrenagem (Settings) no topo superior direito.
* Vá em Resources > WSL Integration.
* Certifique-se de que a opção "Enable integration with my default WSL distro" esteja marcada.
* Abaixo, em "Enable integration with additional distros", ative a chave para o seu Ubuntu.
* Clique em Apply & Restart.

### Primeiro entra no Remote Wsl
* clica em ><, seleciona wsl distro, escolhe o ubuntu

### Command Line
> Crtl+shift+p
* DevContinaer Open folder in container
* Atenção ao nome do container, se repetir da problema

# Instalação do git
> choco install git (Windows)
> git init
> git add .
> git config --global user.email scarlosfreitas@gmail.com
> git config --global user.name "Carlos"
> git commit -m "first commit"
> git branch -M main
> git remote add origin https://github.com/scarlosfreitas/concursos.git
> git branch -M main
> git push -u origin main

# Portainer
> docker volume create portainer_data

# LongChain
> Cria um docker com o langchain e banco sqlite
