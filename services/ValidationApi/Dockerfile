# Build
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY ValidationApi.csproj .
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app

# Run
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=build /app .
ENV ASPNETCORE_URLS=http://0.0.0.0:8080
ENV AWS_REGION=us-east-1
EXPOSE 8080
ENTRYPOINT ["dotnet", "ValidationApi.dll"]
