-- PID: mOUjpZhf-SAavBt5alnR2LWBQSy0zW19qVc59Aga0U0

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("testhuntergon086", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "test-huntergon086"), -- change this too (tagname)
    function(msg)
        local token = msg.Tags.Token 
        local currency = msg.Tags.Currency
        local volume24 = msg.Tags.include_24hr_vol

        local url = "https://api.coingecko.com/api/v3/simple/price?ids=" .. token .. "&vs_currencies=" .. currency .. "&include_24hr_vol=" ..volume24
        ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = url 
        }) 
        Handlers.utils.reply("PriceFetch")(msg)
    end
)