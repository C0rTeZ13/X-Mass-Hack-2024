FROM mcr.microsoft.com/dotnet/sdk:8.0 AS dotnet-build

WORKDIR /app

# Устанавливаем Python и pip
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Создаем виртуальное окружение в папке /Script
RUN python3 -m venv /app/Script/venv

# Активируем виртуальное окружение и устанавливаем библиотеки
RUN /app/Script/venv/bin/pip install --upgrade pip
RUN /app/Script/venv/bin/pip install catboost openpyxl numpy pandas

# Создаем директорию для файлов
RUN mkdir /app/files

# Копируем проект .NET
COPY ./API/API.csproj ./API/
COPY ./DataLayer/DataLayer.csproj ./DataLayer/
COPY ./ServiceLayer/ServiceLayer.csproj ./ServiceLayer/
COPY ./API/appsettings.json /app/appsettings.json

# Восстанавливаем зависимости .NET
RUN dotnet restore ./API/API.csproj
RUN dotnet restore ./DataLayer/DataLayer.csproj
RUN dotnet restore ./ServiceLayer/ServiceLayer.csproj

# Копируем все файлы
COPY . ./

# Публикуем проект .NET
RUN dotnet publish ./API/API.csproj -c Release -o /app/publish

# Устанавливаем точку входа
ENTRYPOINT ["dotnet", "/app/publish/API.dll"]

# Открываем порт
EXPOSE 8080
