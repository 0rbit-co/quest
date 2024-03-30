

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
-- PID = gTbn3r-9wg3dX8GGKZyaUPkIJmILiRvia9IuCHm1KPc
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

Handlers.add("dencuann",
Handlers.utils.hasMatchingTag("Action", "denc-uan"),
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