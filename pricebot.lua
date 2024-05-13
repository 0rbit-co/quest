--- PID = BZvOcmJ1H6XtadQEiKAxKGxVO6M0WopY-Lg4U6EgPME
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

Handlers.add("mrciga",
    Handlers.utils.hasMatchingTag("Action", "mrciga"),
    function(msg)
        local token = msg.Tags.Token
        local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=gbp"
        ao.send({
            Target = _ORBIT,
            Action = "Get-Real-Data",
            Url = url
        })
        Handlers.utils.reply("PriceFetch")
        (msg)
    end
)
