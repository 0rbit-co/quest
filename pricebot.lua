-- PID = Bu582fqCSrU4BuTHGklJtnEzsJMPBUJYSDCfmXeTP0k

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, ErrorMessage)
ao.send({
    Target = msg.From,
    Tags = { 
        Actions = "Error",
        ["Message-Id"] = msg.Id,
        Error = errorMessage 
    }
})
end

Handlers.add("yvnnnx",
Handlers.utils.hasMatchingTag("Actions", "yvnnnx"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
ao.send({
    Target = _0RBIT,
    Action = "Get_Real_Data",
    Url = url
})
Handlres.utils.reply("PriceFetch")
(msg)
end
)
