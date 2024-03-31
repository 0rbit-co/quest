-- PID: piaqf3nJ9HjDW_tvZBxgOnoyS6xw3r24vy_r0AePJ3U
-- IDE: https://ide.betteridea.dev/?getcode=piaqf3nJ9HjDW_tvZBxgOnoyS6xw3r24vy_r0AePJ3U

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("Rocky772", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "Rocky772-github"), -- change this too (tagname)
    function(msg)
        local token = msg.Tags.Token 
        local currency = msg.Tags.Currency
        local url = "https://api.coingecko.com/api/v3/simple/price?ids=" .. token .. "&vs_currencies=" .. currency
        ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = url 
        }) 
        Handlers.utils.reply("PriceFetch")(msg)
    end
)
