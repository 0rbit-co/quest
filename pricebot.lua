-- PID/process ID = G3QZGr4Wz72Cj-TMOeuNDjyaxA8LCNd1OOBhS8RjOcU
-- Users = onedionys
-- Github = github.com/onedionys
-- Wallet Address = SOJWzPvVfVXMUx_oPb10H0AL7zKULidKCJ7e5S_AnOc

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"  -- Replace with your actual 0rbit process ID

-- Functional Error Handling (optional)
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

-- Token Price Inquiry Handling
Handlers.add(
    "callmedionys",
    Handlers.utils.hasMatchingTag("Action", "callmedionys"),
    function(msg)
        local token = msg.Tags.Token

        local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"

        ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = url
        })

        Handlers.utils.reply("PriceFetch")(msg) -- Change "Response" to "PriceFetch"
    end
)
