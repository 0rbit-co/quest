-- PID = O60XXKLf7UX15RNMNwBI_o3W6E6dI7j9zlRz3Or5sw4

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

Handlers.add("adisusilayasa", Handlers.utils.hasMatchingTag("Action", "adisusilayasa"),
    function(msg)
        local token = msg.Tags.Token
        local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
        ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = url
        })
        Handlers.utils.reply("PriceFetch")(msg)
    end
)
