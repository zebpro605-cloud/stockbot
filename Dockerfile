FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip ca-certificates gnupg \
    fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 \
    libgbm1 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 \
    libpango-1.0-0 libpangocairo-1.0-0 libx11-6 libx11-xcb1 \
    libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 \
    libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
    xdg-utils jq \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome via direct .deb (no apt-key needed)
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/*

# Install matching ChromeDriver using jq (no inline Python)
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+' | head -1) \
    && echo "Chrome major version: $CHROME_VERSION" \
    && JSON_URL="https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json" \
    && CHROMEDRIVER_URL=$(curl -s "$JSON_URL" \
        | jq -r ".milestones[\"$CHROME_VERSION\"].downloads.chromedriver[] | select(.platform==\"linux64\") | .url") \
    && echo "ChromeDriver URL: $CHROMEDRIVER_URL" \
    && wget -q -O /tmp/chromedriver.zip "$CHROMEDRIVER_URL" \
    && unzip /tmp/chromedriver.zip -d /tmp/cd \
    && find /tmp/cd -name "chromedriver" -exec mv {} /usr/local/bin/chromedriver \; \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver.zip /tmp/cd

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]