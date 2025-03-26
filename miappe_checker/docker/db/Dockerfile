FROM postgres:15

# Set environment variables
ENV POSTGRES_DB=miappe
ENV POSTGRES_USER=miappe_user
ENV POSTGRES_PASSWORD=miappe_password

# Copy initialization scripts
COPY init.sql /docker-entrypoint-initdb.d/

# Expose the PostgreSQL port
EXPOSE 5432 