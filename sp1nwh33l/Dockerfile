# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS builder

WORKDIR /app

# Copy project file
COPY sp1nwh33l.csproj ./

# Restore dependencies
RUN dotnet restore

# Copy source code
COPY . ./

# Publish the application
RUN dotnet publish -c Release -o /app/publish

# Final stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine

RUN apk --no-cache add ca-certificates curl

WORKDIR /root/

# Copy the published application
COPY --from=builder /app/publish ./

# Expose port
EXPOSE 6007

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=30s \
  CMD curl -f http://localhost:6007/ || exit 1

# Run the application
CMD ["dotnet", "sp1nwh33l.dll"]
