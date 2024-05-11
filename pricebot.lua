-- PID = 1eWvQZw20gRGRD6y56qQVhrUafbOAvA2Vl4xfYdWv5g    

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
Handlers.add("QUEST",
Handlers.utils.hasMatchingTag("Action","QUEST"), function(msg)
local token = msg.Tags.Token
local url = "http://api.coingecko.com/api/v3/simple/price".."?ids"..token.."&vs_currencies=usd"
ao.send({
    Target = _ORBIT,
    Action = "Get-Real-Data",
    Url = url 
})
Handlers.utils.reply("PriceFetch")
(msg)
end 
)
