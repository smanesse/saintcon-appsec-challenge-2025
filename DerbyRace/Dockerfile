# Stage 1: Build frontend
FROM node:24-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Build final image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    gcc \
    libcjson-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Build and install Mongoose from source
RUN wget https://github.com/cesanta/mongoose/archive/7.13.tar.gz \
    && tar xzf 7.13.tar.gz \
    && cd mongoose-7.13 \
    && gcc -shared -fPIC -o libmongoose.so mongoose.c \
    && cp libmongoose.so /usr/local/lib/ \
    && cp mongoose.h /usr/local/include/ \
    && ldconfig \
    && cd .. \
    && rm -rf mongoose-7.13 7.13.tar.gz

WORKDIR /app
COPY derby.c ./
COPY --from=frontend-builder /app/frontend/dist ./static

RUN gcc -fno-stack-protector -z execstack derby.c -L/usr/local/lib -lmongoose -lcjson -lm -o derby

CMD ["./derby"]
