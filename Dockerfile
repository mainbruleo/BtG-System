# 1. Imagem base leve com Python 3.10
FROM python:3.10-slim

# 2. Dependências do sistema para Interface Gráfica e Imagens
RUN apt-get update && apt-get install -y \
    python3-tk \
    libtk8.6 \
    libpng-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Diretório de trabalho
WORKDIR /app

# 4. Instalação de dependências (corrigido para requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia o código fonte
COPY . .

# 6. Variável de ambiente para o servidor X11
ENV DISPLAY=:0

# 7. Execução
CMD ["python", "BtGSys.py"]