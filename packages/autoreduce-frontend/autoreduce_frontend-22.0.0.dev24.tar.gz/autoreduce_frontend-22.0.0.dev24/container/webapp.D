FROM ghcr.io/autoreduction/base

# Installs frontend from your local repository
ADD . .
RUN python3 -m pip install --user --no-cache-dir .

# Add fixtures to the project for dev/debugging
ADD --chown=isisautoreduce:isisautoreduce autoreduce_frontend/autoreduce_webapp/fixtures/ fixtures/ 

USER root
RUN mkdir -p /var/www/api/
RUN chown isisautoreduce:isisautoreduce /var/www/api/
USER isisautoreduce

EXPOSE 8000
CMD ["autoreduce-webapp-manage", "serve", "--port", "8000", "--probe-port", "8004"]
