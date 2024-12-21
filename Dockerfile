FROM mcr.microsoft.com/dotnet/sdk:8.0

WORKDIR /app

COPY ./API/API.csproj ./API/
COPY ./DataLayer/DataLayer.csproj ./DataLayer/
COPY ./ServiceLayer/ServiceLayer.csproj ./ServiceLayer/
COPY ./API/appsettings.json /app/appsettings.json

RUN dotnet restore ./API/API.csproj
RUN dotnet restore ./DataLayer/DataLayer.csproj
RUN dotnet restore ./ServiceLayer/ServiceLayer.csproj

COPY . ./

RUN dotnet publish ./API/API.csproj -c Release -o /app/publish

ENTRYPOINT ["dotnet", "/app/publish/API.dll"]

EXPOSE 8080
