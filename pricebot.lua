-- PID: W64ddAJpAH5axzZ3FYvAOsf11gkWiAhsQggqoGZ2vTk
-- IDE: https://ide.betteridea.dev/?getcode=W64ddAJpAH5axzZ3FYvAOsf11gkWiAhsQggqoGZ2vTk

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("erikamin",
    Handlers.utils.hasMatchingTag("Action", "erika-min"),
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
