// Fase C - API minimo para medir performance de lectura/escritura en DynamoDB.
//
// No es el microservicio de validacion completo de CU-03 (esa es una fase de
// implementacion de computo mas amplia, fuera del alcance de esta actividad).
// Es un arnes de medicion: aisla las dos operaciones que la Actividad 1 pide
// medir ("consumo de lectura y/o escritura"), sin la logica de negocio
// completa (verificacion de lista negra, saldo, anti-passback, lista blanca),
// para que JMeter mida la latencia real de GetItem/PutItem contra la tabla.

using Amazon.DynamoDBv2;
using Amazon.DynamoDBv2.Model;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<IAmazonDynamoDB>(_ =>
{
    var region = Environment.GetEnvironmentVariable("AWS_REGION") ?? "us-east-1";
    return new AmazonDynamoDBClient(Amazon.RegionEndpoint.GetBySystemName(region));
});

var app = builder.Build();

// Lectura: GetItem por Partition Key (camino critico de validacion).
app.MapGet("/cards/{cardId}", async (string cardId, IAmazonDynamoDB dynamoDb) =>
{
    var sw = System.Diagnostics.Stopwatch.StartNew();
    var response = await dynamoDb.GetItemAsync(new GetItemRequest
    {
        TableName = "Cards",
        Key = new Dictionary<string, AttributeValue>
        {
            ["cardId"] = new AttributeValue { S = cardId }
        }
    });
    sw.Stop();

    if (response.Item is null || response.Item.Count == 0)
    {
        return Results.NotFound(new { error = "not_found", cardId });
    }

    return Results.Ok(new
    {
        item = response.Item.ToDictionary(kv => kv.Key, kv => kv.Value.S ?? kv.Value.N),
        dynamodbMs = sw.Elapsed.TotalMilliseconds
    });
});

// Escritura: PutItem en ValidationLog (evento de validacion).
app.MapPost("/validations", async (ValidationRequest req, IAmazonDynamoDB dynamoDb) =>
{
    var now = DateTimeOffset.UtcNow;
    var ttl = now.AddDays(400).ToUnixTimeSeconds();

    var item = new Dictionary<string, AttributeValue>
    {
        ["cardId"] = new AttributeValue { S = req.CardId ?? $"CARD-{Guid.NewGuid():N}"[..13] },
        ["timestamp"] = new AttributeValue { S = now.ToString("yyyy-MM-ddTHH:mm:ss.fffZ") },
        ["deviceId"] = new AttributeValue { S = req.DeviceId ?? "PERF-TEST-DEVICE" },
        ["deviceType"] = new AttributeValue { S = req.DeviceType ?? "STATION" },
        ["result"] = new AttributeValue { S = "ALLOW" },
        ["reasonCode"] = new AttributeValue { S = "OK" },
        ["balanceAfter"] = new AttributeValue { N = "0" },
        ["ttl"] = new AttributeValue { N = ttl.ToString() },
    };

    var sw = System.Diagnostics.Stopwatch.StartNew();
    await dynamoDb.PutItemAsync(new PutItemRequest
    {
        TableName = "ValidationLog",
        Item = item
    });
    sw.Stop();

    return Results.Created($"/validations/{item["cardId"].S}", new
    {
        cardId = item["cardId"].S,
        timestamp = item["timestamp"].S,
        dynamodbMs = sw.Elapsed.TotalMilliseconds
    });
});

app.MapGet("/health", () => Results.Ok(new { status = "ok" }));

app.Run();

record ValidationRequest(string? CardId, string? DeviceId, string? DeviceType);
