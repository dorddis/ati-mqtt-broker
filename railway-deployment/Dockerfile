# Railway MQTT Broker Dockerfile
# Optimized for ATI integration hosting

FROM eclipse-mosquitto:2.0.18

# Set Railway-friendly user
USER root

# Create necessary directories
RUN mkdir -p /mosquitto/data /mosquitto/log /mosquitto/config

# Copy configuration files
COPY mosquitto/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY mosquitto/passwd /mosquitto/config/passwd
COPY mosquitto/acl.conf /mosquitto/config/acl.conf

# Set proper permissions
RUN chown -R mosquitto:mosquitto /mosquitto/data /mosquitto/log /mosquitto/config
RUN chmod 600 /mosquitto/config/passwd /mosquitto/config/acl.conf

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --retries=3   CMD mosquitto_pub -h localhost -p 1883 -t health/check -m "ok" || exit 1

# Expose ports
EXPOSE 1883 9001

# Use mosquitto user
USER mosquitto

# Start mosquitto with custom config
CMD ["mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
