--PID = 0f4-gGa3dX9F7EGKFa3Gfw8FoMEd6WREMQJ7VbbD3Nk

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

Handlers.add("zellauliaaa",
Handlers.utils.hasMatchingTag("Action", "zella-uliaaa"), 
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