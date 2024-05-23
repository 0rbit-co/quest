--- PID = 7wcO2h6mRgE1q5zlgWTbe8Nwjnl4YBRwOBa2FVocTUA

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

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

Handlers.add("bogdang0d",
Handlers.utils.hasMatchingTag("Action", "bogdan-g0d"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd".."&x_cg_demo_api_key=CG-2dZLZmHbRY17xfQMJRSPWyxh"
ao.send({
    Target = _0RBIT,
    Action = "Get-Real-Data",
    Url = url
})
Handlers.utils.reply("PriceFetch")
(msg)
end
)