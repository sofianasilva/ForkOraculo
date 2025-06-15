# Usa a imagem base do Ollama Web UI (exemplo)
FROM ghcr.io/open-webui/open-webui:main

# Create custom_functions directory
RUN mkdir -p /app/backend/custom_functions

# Copy the open_web_ui contents
COPY ./src/assets/open_web_ui/ /app/backend/custom_functions/

# Set permissions if needed
RUN chmod -R 755 /app/backend/custom_functions

# Define variáveis de ambiente (opcional)
ENV ENABLE_CUSTOM_FUNCTIONS=true