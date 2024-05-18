-- PID: jYqd1JNB6tvMwD9nwG9UdP7_80Yz-Xtq65T5-kj0Pso
-- IDE: https://ide.betteridea.dev/?getcode=jYqd1JNB6tvMwD9nwG9UdP7_80Yz-Xtq65T5-kj0Pso

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("budalebah", 
    Handlers.utils.hasMatchingTag("Action", "budalebah-github"), 
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
