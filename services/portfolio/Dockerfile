# estágio 1: gera o site
FROM hugomods/hugo:exts-0.154.5 AS build
WORKDIR /src
COPY site/ .
RUN hugo --minify

# estágio 2: serve os arquivos
FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /src/public /usr/share/caddy
