FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y apache2 php8.2 php8.2-mysqli mariadb-server
COPY ./src/html/ /var/www/html/
COPY ./src/db/seed.sql /tmp/seed.sql
# In a full build, the entrypoint script would start MariaDB, run seed.sql, and start Apache.
