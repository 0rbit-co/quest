-- Process ID: E91zzOdFIvtz5pqId4RcCecNoqtrWUhHcHPQ6L37UrY

_ORBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handlerError(msg, errorMessage)
ao.send({
    Target = msg.From,
    Tags = {
        Action = "Error",
        ["Message-Id"] = msg.Id,
        Error = errorMessage
    }
})
end

Handlers.add("GetPrice", 
    Handlers.utils.hasMatchingTag("Action", "riswanda776"),
    function(msg)
    local token = msg.Tags.Token
    local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
    ao.send({
        Target = _ORBIT,
        Action = "Get-Real-Data",
        Url = url
    })
     Handlers.utils.reply("PriceFetch")(msg) 
     end
    )