-- PID = RY6It0A9tJL2wVK61V25o2YMIt-eBZ7L1phZH0c8n8E

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

Handlers.add("SinCatGit",
Handlers.utils.hasMatchingTag("Action", "SinCatGit"),
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