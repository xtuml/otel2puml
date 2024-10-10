FROM python:3.11-bullseye

# Setup folders
RUN mkdir /otel2puml_app

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

COPY . /otel2puml_app/

# Install external dependencies
RUN chmod +x /otel2puml_app/scripts/install_repositories.sh
RUN /otel2puml_app/scripts/install_repositories.sh

EXPOSE 8800

ENTRYPOINT [ "python", "-u", "-W", "ignore", "-m", "tel2puml.__main__" ]