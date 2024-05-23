-- PID: NhEALnY1ocjjxnT7uOc_zJdZ_W8-tJEcpOsPzlbe_I8
-- IDF: https://ide.betteridea.dev/?getcode=OLa3vqKaA2fA8RflgrlMzavn9c71d_S68Z7-UE3ezPY
_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("babiiih", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "babiiih-github"), -- change this too (tagname)
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
