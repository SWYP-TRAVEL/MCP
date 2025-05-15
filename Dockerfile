# ===== 1단계: 빌더 스테이지 =====
FROM python:3.12-slim AS builder

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# UV 설치
RUN pip install --no-cache-dir uv

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치
RUN uv pip install --system -r pyproject.toml

# ===== 2단계: 런타임 스테이지 =====
FROM python:3.12-slim

WORKDIR /app

# 런타임에 필요한 최소 패키지 설치
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 빌드된 패키지 복사
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock ./

# app 전체 복사 (app 디렉토리 내부가 /app/app이 아닌 /app/app으로 들어가도록)
COPY app/ ./app/

# .env 파일 복사 (존재하면)
COPY .env* ./

# 포트 노출
EXPOSE 8077 8070 8071

# 유저 추가
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app

# 실행 스크립트 작성
RUN echo '#!/bin/bash\n\
python3 ./app/main.py &\n\
python3 -m app.create.server &\n\
python3 -m app.triplet.server &\n\
wait' > /app/start.sh && chmod +x /app/start.sh

USER mcpuser

# 컨테이너 실행 시 모든 서비스 시작
CMD ["/app/start.sh"]