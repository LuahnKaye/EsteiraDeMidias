FROM nginx:1.25-alpine

# Remove o arquivo de configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia a nossa configuração customizada otimizada
COPY nginx.conf /etc/nginx/conf.d/

# Copia o código estático do Frontend SPA (HTML, CSS e JS)
COPY src/ /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
