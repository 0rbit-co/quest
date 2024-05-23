-- PID: fO8c9Ol4HOshWxUEXmEjJUlRnnFzQk0oq0IMu1Lp6og
-- IDE: https://ide.betteridea.dev/?getcode=fO8c9Ol4HOshWxUEXmEjJUlRnnFzQk0oq0IMu1Lp6og

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("oxrafy",
    Handlers.utils.hasMatchingTag("Action", "oxrafy-github"),
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
