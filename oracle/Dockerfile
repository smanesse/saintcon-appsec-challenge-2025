FROM openjdk:21-jdk-slim

# Install sbt and curl (needed for healthcheck)
RUN apt-get update && \
    apt-get install -y curl && \
    curl -L "https://github.com/sbt/sbt/releases/download/v1.9.6/sbt-1.9.6.tgz" | tar xz -C /opt && \
    ln -s /opt/sbt/bin/sbt /usr/local/bin/sbt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy build files first for better caching
COPY build.sbt .
COPY project/ project/

# Download dependencies
RUN sbt update

# Copy source code
COPY . .

# Build the application
RUN sbt compile stage

# Expose port
EXPOSE 6004

# Run the application
CMD ["target/universal/stage/bin/number-guessing-game", "-Dhttp.port=6004", "-Dhttp.address=0.0.0.0"]
