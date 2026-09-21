FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y apache2 php8.2 php8.2-mysqli
COPY ./src/html/ /var/www/html/
CMD ["apache2ctl", "-D", "FOREGROUND"]