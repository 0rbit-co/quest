-- PID = ehKcynShdlolyJqgm-233xoOpa_fah_alzGOB4A0YJc

_0RBIT="WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function errorHandling(msg, errMsg)
ao.send({
    Target = msg.From,
    Tags = {
        Action = "Error",
        ["Message-Id"] = msg.Id,
        Error = errMsg
    }
})
end

Handlers.add("sutanarief",
Handlers.utils.hasMatchingTag("Action", "sutan-arief"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
ao.send({
    Target = _0RBIT,
    Action = "Get-Real-Data",
    Url = url
})
Handlers.utils.reply("Fetching Price")
(msg)
end
)