FROM rust:1 AS chef
RUN cargo install cargo-chef
WORKDIR /app

FROM chef AS frontend-planner
COPY itrivia-app/ .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS frontend-builder
COPY --from=frontend-planner /app/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json
COPY itrivia-app/ .

RUN curl -L --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/cargo-bins/cargo-binstall/main/install-from-binstall-release.sh | bash
RUN cargo binstall dioxus-cli --root /.cargo -y --force --locked
ENV PATH="/.cargo/bin:$PATH"

RUN dx build --release

FROM fukamachi/sbcl:latest-debian AS packages

RUN apt-get update && apt-get install -y \
    libev-dev \
    build-essential \
    curl \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -O https://beta.quicklisp.org/quicklisp.lisp
RUN sbcl --load ./quicklisp.lisp --eval "(quicklisp-quickstart:install)"
RUN sbcl --eval "(ql:quickload '(:clack :woo :cffi :lack :alexandria :flexi-streams :log4cl :com.inuoe.jzon))"

WORKDIR /app

COPY --from=frontend-builder /app/target/dx/itrivia-app/release/web/public ./public/

COPY server.lisp ./

RUN touch itrivia.db

RUN echo '#!/bin/bash\nsbcl --load server.lisp --eval "(loop (sleep 1))"' \
  > start.sh && chmod +x start.sh

EXPOSE 6006

ENTRYPOINT ["./start.sh"]