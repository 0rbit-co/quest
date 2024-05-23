-- PID = Ob_QTM4r0o8z_jJo6SwmwoprUEopi7gzEuGnwbnTwwg

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, errorMessage)
ao.send ({
    Target = msg.Form,
    Tags = {
        Action = "Error",
        ["Message-Id"] = msg.Id,
        Error = errorMessage
    }
})
end

Handlers.add("morankzpande",
Handlers.utils.hasMatchingTag("Action", "morankz-pande"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price".."?ids="..token.."&vs_currencies=usd"
ao.send ({
    Target = _0RBIT,
    Action = "Get-Real-Data",
    Url = url
})
Handlers.utils.reply ("PriceFetch")
(msg)
end
)