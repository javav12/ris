FROM alpine:3.18 AS builder

# 1. install dependencies
RUN apk add --no-cache \
    build-base \
    python3 \
    python3-dev \
    py3-pip \
    musl-dev \
    linux-headers \
    binutils \
    ccache \
    wget \
    tar \
    xz \
    bash \
    git \
    autoconf \
    automake \
    libtool

# 2. install patchelf
RUN git clone https://github.com/NixOS/patchelf.git /tmp/patchelf && \
    cd /tmp/patchelf && \
    git checkout 0.17.2 && \
    ./bootstrap.sh && \
    ./configure --prefix=/usr && \
    make && make install && \
    rm -rf /tmp/patchelf

# 3. install zig
RUN mkdir -p /usr/local/zig && \
    wget -q https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.1158+1d1193aa7.tar.xz -O /tmp/zig.tar.xz && \
    tar -xf /tmp/zig.tar.xz -C /usr/local/zig --strip-components=1 && \
    rm /tmp/zig.tar.xz

ENV PATH="/usr/local/zig:${PATH}"

# Check Zig version to ensure it's installed correctly
RUN zig version

# 4. Set up the working directory and install Python dependencies
WORKDIR /app
COPY requirements.txt ./requirements.txt

# Create a virtual environment and install dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# copy source code
COPY src/ ./src/

# 5. compile the Python code to a static binary using Nuitka
ENV LDFLAGS="-static -Wl,-Bstatic"
RUN mkdir -p build && \
    nuitka --standalone --static-libpython=yes --zig --output-dir=/dist src/main.py && \
    cp /dist/main.dist/main.bin build/main.bin

FROM scratch
COPY --from=builder /app/build/main.bin /app_binary
ENTRYPOINT ["/app_binary"]
