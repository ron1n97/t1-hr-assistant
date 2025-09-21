# Frontend Dockerfile для разработки
FROM node:18

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json (если есть)
COPY package*.json ./

# Устанавливаем зависимости с правильными флагами
RUN npm install --legacy-peer-deps

# Копируем исходный код
COPY . .

# Открываем порт
EXPOSE 3000

# Команда для запуска в режиме разработки
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
