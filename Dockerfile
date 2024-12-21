FROM python:3.12 AS python-build

WORKDIR /app/Script

COPY Script/pyproject.toml ./

RUN pip install poetry
RUN poetry cache clear --all pypi
RUN poetry install -vvv

ENV PYTHONPATH="/app:${PYTHONPATH}"

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS dotnet-build

WORKDIR /app

RUN mkdir /files

COPY --from=python-build /app /app/Script

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
