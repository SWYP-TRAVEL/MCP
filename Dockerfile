# Multi-stage Dockerfile for MCP Services
FROM python:3.12-slim AS builder

WORKDIR /app

# 시스템 패키지 업데이트 및 빌드 의존성 설치
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# UV 설치
RUN pip install --no-cache-dir uv

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (빌드 단계)
RUN uv pip install --system -r pyproject.toml

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# 런타임에 필요한 최소한의 패키지만 설치
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 빌드 단계에서 설치한 패키지 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock ./

# 애플리케이션 코드 복사
COPY app/ ./app/

# 환경 변수 설정을 위한 .env 파일 복사 (있는 경우)
COPY .env* ./

# 포트 노출 (모든 서비스가 사용하는 포트)
EXPOSE 8000 8070 8071

# 비루트 사용자 생성 및 전환
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# 기본 커맨드는 docker-compose에서 오버라이드됨
CMD ["python", "-m", "app.main"]
