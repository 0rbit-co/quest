-- PID: oQQeiEMINZ3c12DZ0-ziYhmKcn2fFmGkqZpyqQZOu40
-- IDE: https://ide.betteridea.dev/?getcode=oQQeiEMINZ3c12DZ0-ziYhmKcn2fFmGkqZpyqQZOu40

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("semutireng22", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "semutireng22-github"), -- change this too (tagname)
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
