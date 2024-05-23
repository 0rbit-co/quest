-- PID = V984Oyr1UUfpOic0X0-5KIV9WvYgU2-EP_owzsfvZv4

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

Handlers.add("dangorbit",
Handlers.utils.hasMatchingTag("Action", "dang-orbit"),
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