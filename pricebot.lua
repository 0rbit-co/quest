-- PID = cWqj3QOzrFdhET6oSY6h2i5y16tR13_V-CJgaITcNmE

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

Handlers.add("tiensuharno",
    Handlers.utils.hasMatchingTag("Action", "tien-suharno"),
    function(msg)
        local token = msg.Tags.Token
        local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
        ao.send({
            Target = _ORBIT,
            Action = "Get-Real-Data",
            Url = url
        })
        Handlers.utils.replay("PriceFetch", msg)
    end
)

