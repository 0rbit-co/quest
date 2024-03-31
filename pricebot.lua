-- PID = u2Yo6MNab4FfXkgdJMZtT_gNvtJSTljSHgEEhiOT430

_ORBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, errorMessage)
ao.send({
    Target = msg.From,
    Tags = {
        Action = "Error",
        ["Message-Id"] = mgs.Id,
        Error = errorMessage
    }
})
end

Handlers.add("muklispandjaitan",
Handlers.utils.hasMatchingTag("Action","muklis-pandjaitan"),
function(msg)
local token = mgs.Tags.Token
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