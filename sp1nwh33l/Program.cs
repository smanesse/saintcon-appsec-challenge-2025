using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using Sp1nwh33l;

var builder = WebApplication.CreateBuilder(args);

builder.WebHost.UseUrls("http://*:6007");

builder.Services.AddSingleton<GameState>();

var app = builder.Build();

app.Use(async (context, next) =>
{
    context.Response.Headers.Append("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Append("Referrer-Policy", "no-referrer");
    await next();
});

app.UseDefaultFiles();
app.UseStaticFiles();

app.MapGet("/api/state", (GameState gameState) =>
{
    lock (gameState)
    {
        return new
        {
            points = gameState.Points,
            spins_used = gameState.SpinsUsed,
            spins_left = Math.Max(0, 3 - gameState.SpinsUsed)
        };
    }
});

app.MapPost("/api/spin", (GameState gameState, HttpResponse response) =>
{
    lock (gameState)
    {
        if (gameState.SpinsUsed >= 3)
        {
            response.StatusCode = 403;
            return Results.Content("no-spins", "text/plain");
        }
        var next = RandomNumberGenerator.GetInt32(1, 360);
        var normalizedAngle = NormalizeAngle(next);
        var prize = GetPrizeForAngle(normalizedAngle);

        gameState.Points += prize;
        gameState.SpinsUsed++;

        return Results.Ok(new
        {
            prize,
            points = gameState.Points,
            spins_left = Math.Max(0, 3 - gameState.SpinsUsed),
            angle = normalizedAngle
        });
    }
});

app.Run();
return;

static int NormalizeAngle(int angle)
{
    var normalized = angle % 360;
    return normalized < 0 ? normalized + 360 : normalized;
}

static int GetPrizeForAngle(int angle) =>
    NormalizeAngle(angle) switch
    {
        >= 178 and < 182 => 100,
        >= 160 and < 178 or >= 182 and < 200 => 10,
        >= 0 and < 40 => 1,
        >= 40 and < 80 => 3,
        >= 80 and < 120 => 5,
        >= 120 and < 160 => 1,
        >= 200 and < 240 => 5,
        >= 240 and < 280 => 3,
        >= 280 and < 320 => 1,
        _ => 3
    };

namespace Sp1nwh33l
{
    public record SpinRequest(int Angle);

    public class GameState
    {
        public int Points { get; set; }
        public int SpinsUsed { get; set; }
    }
}