# Usar imagem mais recente e segura
FROM python:3.13-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar bibliotecas do sistema necessárias para o OpenCV
RUN apt-get update && apt-get install -y \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar dependências e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar a aplicação
COPY . .

# Criar pasta de uploads (caso não exista)
RUN mkdir -p uploads

# Expor a porta do Flask
EXPOSE 5000

# Comando de inicialização
CMD ["python", "app.py"]
