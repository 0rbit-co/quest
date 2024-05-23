-- PID = ZK2c1FhsB_TmHggEQCreV9jcoYFt4pPwOcysDC9oCMo
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

Handlers.add("dlzvy",
Handlers.utils.hasMatchingTag("Action", "dlzvy-eth1"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?isd=" .. token .. "&vs_currencies=usd"
ao.send ({
    Target = _ORBIT,
    Action = "Get-Real-Data",
    Url = url
})
Handlers.utils.reply("PriceFetch")
(msg)
end
)