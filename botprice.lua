-- PID = kMXeX4XXaYckNatK_P-HWMdx2h29eV8Fa8eMHcdYaPI

_ORBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, errorMessage)
ao.send({
    Tareget = msg.From,
    Tags = {
        Action = "Error" ,
        ["Message-Id"] = msg.Id,
        Error = Message
    }
})
end

Handlers.add("kipli",
Handlers.utils.hasMatchingTag("Action", "kipli"),
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