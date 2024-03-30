-- PID = cuM-AfWPJlKb2QXNbqm50i4AR8-UBwF-xx8QSEghRwI

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, errorMessage)
ao.send({
    Target = msg.From,
    Tags = {
        Action = "Error",
        ["Message-Id"] = msg.id,
        Error = errorMessage
    }
})
end

Handlers.add("ryzwan29",
Handlers.utils.hasMatchingTag("Action", "ryzwan-29"),
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