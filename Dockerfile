FROM python:3.11-bullseye

# Setup folders
RUN mkdir /otel2puml_app && mkdir /otel2puml_app/tel2puml

WORKDIR /otel2puml_app

# Install system dependencies needed for cvxopt
RUN apt-get update && apt-get install -y \
    liblapack-dev \
    libopenblas-dev \
    libsuitesparse-dev \
    libglpk-dev \
    && apt-get clean

# Set environment variables for cvxopt build
ENV CPPFLAGS="-I/usr/include/suitesparse"
ENV CVXOPT_BUILD_GLPK=1
ENV PYTHONUNBUFFERED=1

# Caches packages installed by pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./tel2puml/ /otel2puml_app/tel2puml/
COPY ./scripts/install_repositories.sh /otel2puml_app/

# Create a non-root user and give ownership of the app folder
RUN useradd -m otel2pumluser && chown -R otel2pumluser /otel2puml_app

# Switch to the non-root user
USER otel2pumluser

# Install external dependencies
RUN chmod +x /otel2puml_app/install_repositories.sh
RUN /otel2puml_app/install_repositories.sh

EXPOSE 8800

ENTRYPOINT [ "python", "-m" ]