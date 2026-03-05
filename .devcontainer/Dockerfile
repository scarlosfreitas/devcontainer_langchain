FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libgbm1 \    
    && rm -rf /var/lib/apt/lists/*


# 1. Instala as dependências necessárias
RUN apt-get update && apt-get install -y curl gnupg2 software-properties-common

# 2. Baixa a chave GPG do Google e converte para o formato que o novo APT exige
RUN curl -fSsL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /usr/share/keyrings/google-chrome.gpg > /dev/null

# 3. Adiciona o repositório referenciando especificamente essa chave
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# 4. Instala o Chrome
RUN apt-get update && apt-get install -y google-chrome-stable