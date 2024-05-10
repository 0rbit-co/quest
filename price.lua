-- PID: mLnxJ7ixa_WBx2b_OWMcTAP6QYFqwbE5m7ijo6zhvZ0
-- IDE: https://ide.betteridea.dev/?getcode=mLnxJ7ixa_WBx2b_OWMcTAP6QYFqwbE5m7ijo6zhvZ0

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("agusbopeng", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "agusbopeng-github"), -- change this too (tagname)
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
