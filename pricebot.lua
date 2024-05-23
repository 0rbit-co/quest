--PID = 8nuu0eRSKvEAyjBW1UgOxbbO4tsJi1mJAX9qRsiv5aw

_0RBIT = "Tts9C1YX67DYyGEMX-7uhDNJkXf0QpPIlNUJOtTGyFQ"

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

Handlers.add("projek",
Handlers.utils.hasMatchingTag("Action", "projek"),
function(msg)
local token = msg.Tags.Token
local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
ao.send({
    Target = _0RBIT,
    Action = "Get-Real-Data",
    Url = url
})
Handlers.utils.reply("PriceFetch")
(msg)
end
)