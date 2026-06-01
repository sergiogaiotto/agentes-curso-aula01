# Imagem base enxuta com Python 3.12
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala as dependências primeiro (aproveita o cache de build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY ./app ./app

# O Render injeta a porta na variável $PORT. --host 0.0.0.0 é obrigatório
# para o serviço aceitar tráfego externo. Usamos a exec form (lista) do CMD.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
