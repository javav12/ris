!#/bin/bash
# 1. İmajı build et
docker build -t static-app-image .

# 2. İmajdan dosyayı geçici bir container oluşturup dışarı kopyala
docker create --name temp-container static-app-image
docker cp temp-container:/app_binary ./build/main.bin
docker rm temp-container

