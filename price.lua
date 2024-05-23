-- PID: PLzclqh_DduoQTDRJ9S1bgF95qG26eE0Rvw5pt6CGWA
-- IDE: https://ide.betteridea.dev/?getcode=PLzclqh_DduoQTDRJ9S1bgF95qG26eE0Rvw5pt6CGWA

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("iqbaldsw", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "iqbaldsw-github"), -- change this too (tagname)
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
