-- PID: NhEALnY1ocjjxnT7uOc_zJdZ_W8-tJEcpOsPzlbe_I8
-- IDE: https://ide.betteridea.dev/?getcode=n275DeGEWpTpbxA6ryzXjo1iykOK7_OQMXQGDYJ-L3M

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("Canarias96", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "Canarias96-github"), -- change this too (tagname)
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
