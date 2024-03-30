-- PID = 0sktWgCztzX58wq8o0KNNEK0afaYnaYkcav3RELuDHk
_ORBIT ="WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(ms, errorMessage)
ao.send({
    Target = msg.From,
    Tags = {
        Action = "error",
        ["Message-Id"] = msg.Id,
        Error = errorMessage
    }
})
end

Handlers.add("netvalidx",
Handlers.utils.hasMatchingTag("Action", "aliffahrijal"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=".. token .. "&vs_currencies=usd"
ao.send({
    Target = _ORBIT,
    Action = "Get-Real-Data",
    Url = url
})

Handlers.utils.reply("PriceFetch")
(msg)
end
)