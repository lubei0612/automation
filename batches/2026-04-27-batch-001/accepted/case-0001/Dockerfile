
# 基础镜像：Ubuntu 22.04
FROM --platform=linux/amd64 ubuntu:22.04

LABEL org.opencontainers.image.ref.name=ubuntu
LABEL org.opencontainers.image.version=22.04
# 避免APT等工具在构建过程中请求交互式输入
ENV DEBIAN_FRONTEND=noninteractive

# 1. 基础环境配置：安装必要的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # --- 通用工具 ---
    wget \
    git \
    ca-certificates \
    curl \
    vim \
    dos2unix \
    # --- Python 基础 ---
    python3 \
    python3-pip \
    python-is-python3 \
    nodejs \
    npm \
    build-essential 

# 2. 安装Miniconda3（Python 3.11）
RUN arch="$(uname -m)" && \
    case "$arch" in \
      x86_64) miniconda_arch="x86_64" ;; \
      aarch64|arm64) miniconda_arch="aarch64" ;; \
      *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
    esac && \
    wget "https://repo.anaconda.com/miniconda/Miniconda3-py311_23.11.0-2-Linux-${miniconda_arch}.sh" -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/miniconda3 && \
    rm -f miniconda.sh

# 将Miniconda的可执行文件目录添加到系统PATH
ENV PATH=/opt/miniconda3/bin:${PATH}

# 初始化Conda，使其能够在shell脚本中被调用，并配置conda-forge渠道
RUN conda init bash && \
    conda config --add channels conda-forge && \
    conda config --remove channels defaults

# --- 核心修改：先执行 setup_repo.sh 进行 git clone ---
COPY setup_repo.sh /root/setup_repo.sh
RUN chmod +x /root/setup_repo.sh && \
    /bin/bash /root/setup_repo.sh

# --- 然后执行 setup_env.sh 进行依赖安装 ---
COPY setup_env.sh /root/setup_env.sh
RUN chmod +x /root/setup_env.sh && \
    # 在一个已初始化Conda的bash环境中执行脚本
    /bin/bash -c "source /root/.bashrc && /root/setup_env.sh"

COPY code.patch test.patch final.diff run_verification.py /verification/

WORKDIR /testbed
# 修改.bashrc文件，这样当启动交互式bash时，会自动激活'testbed'环境
RUN echo "conda activate testbed" >> /root/.bashrc

CMD ["/bin/bash"]
