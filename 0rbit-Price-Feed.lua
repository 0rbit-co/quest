-- PID = tfX1p-HfqtWjgU32LL7I53-KEWDvQrn7UMfTtkky5I0
-- aos 0rbitPriceFeed --cron 30-seconds --load 0rbit-Price-Feed.lua
-- Send({ Target = ao.id, Action="suclogger", Tags = { Token = "BTC" }})

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

Handlers.add("suclogger",
Handlers.utils.hasMatchingTag("Action", "suclogger"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .."&vs_currencies=usd"
ao.send({
    Target = _ORBIT,
    Action = "Get-Real-Data",
    Url = url
})
Handlers.utils.reply("PriceFetch")
(msg)
end
)
