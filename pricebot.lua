-- PID = LR5t5EptfAJuan5r6A4QCHov6ugx8fXC9-N1kwfMqe0

_0RBIT= "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, errorMessage)
ao.send({
    Target = msg.Form,
    Tags = { 
        Action = "Error",
        ["Message-Id"] = msg.id,
        Error = errorMessage
    }
})
end

Handlers.add("vaioios",
Handlers.utils.hasMatchingTag("Action", "vaioios"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
ao.send({
    Target = _0RBIT,
    Action = "Get-Real-Data",
    Url = url
})
Handlers.utils.reply("PriceFetch")
(msg)
end
)