-- PID = U5ugg0D21Cm2KeWWbe1KhDiG8S5yjdn8Jzy7sSholoU

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, errorMessage)
ao.send({
    Terget = msg.From,
    Tags = {
        Action = "Error",
        ["Message-Id"] = mgs.Id,
        Error = errorMessage
    }
})
end

Handlers.add("oxcel",
Handlers.utils.hasMatchingTag("Action", "oxcel"),
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