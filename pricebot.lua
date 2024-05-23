--PID = d4pFHYA6cKZpG0zeB2l-8VJj7ctVXQ1zYb5XYoYJdxA

_ORBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, errorMessage)
ao.send({
    Target = msg.From,
    Tags = {
        Action = "Error",
        ["Message-Id"] = msg.Id,
        Error = errorMessage
    }
})
end

Handlers.add("desmapradiftaa",
Handlers.utils.hasMatchingTag("Action", "desma-pradiftaa"), 
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
ao.send({
    Target = _ORBIT,
    Action = "Get-Real-Data",
    Url = url 
})
Handlers.utils.reply("PriceFetch")
(msg)
end
)