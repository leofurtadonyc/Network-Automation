# Use a slim Python base image.
FROM python:3.12-slim

# Install OS dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
  && rm -rf /var/lib/apt/lists/*

# Set work directory.
WORKDIR /app

# Clone the IRRd repository.
RUN git clone https://github.com/irrdnet/irrd.git

# Change to the IRRd directory.
WORKDIR /app/irrd

# Install IRRd and its dependencies.
RUN pip install --upgrade pip && pip install .

# Expose the HTTP and Whois ports.
EXPOSE 8080 8043

# Create necessary directories with proper ownership and permissions.
RUN mkdir -p /var/run/irrd && chown daemon:daemon /var/run/irrd
RUN mkdir -p /var/log/irrd && chown daemon:daemon /var/log/irrd && chmod 775 /var/log/irrd

# Copy your configuration file.
COPY irrd.yaml /etc/irrd/irrd.yaml

# Copy the entrypoint script and set it executable using Docker BuildKit's --chmod flag.
COPY --chmod=+x entrypoint.sh /usr/local/bin/entrypoint.sh

# Switch to the 'daemon' user.
USER daemon

# Use the entrypoint script as the container's entrypoint.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Start IRRd in the foreground.
CMD ["sh", "-c", "exec irrd --config /etc/irrd/irrd.yaml --foreground"]
