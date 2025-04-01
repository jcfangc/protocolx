FROM rust:1.85-slim

# 设置工作目录
WORKDIR /app

# 安装构建所需的最小工具（如 curl，用于手动安装 Rye）
# 如果你用 COPY 携带 Rye 安装脚本，也可跳过 curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

# 缺省入口
CMD ["bash"]
