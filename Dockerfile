FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    firefox-esr \
    && rm -rf /var/lib/apt/lists/*

RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        GECKO_URL="https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        GECKO_URL="https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux-aarch64.tar.gz"; \
    else \
        echo "Architecture non supportée: $ARCH" && exit 1; \
    fi && \
    wget $GECKO_URL -O geckodriver.tar.gz && \
    tar -xzf geckodriver.tar.gz && \
    chmod +x geckodriver && \
    mv geckodriver /usr/local/bin/ && \
    rm geckodriver.tar.gz

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -s /bin/bash botuser
RUN chown -R botuser:botuser /app
USER botuser

CMD ["python", "discord_bot_scrapper.py", "--webdriver", "firefox"]