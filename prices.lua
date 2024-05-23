-- PID: hqFfSaaYxOBmLTQG5kYCDS4JG3iF3975-wgDruAKohA
-- IDE: https://ide.betteridea.dev/?getcode=hqFfSaaYxOBmLTQG5kYCDS4JG3iF3975-wgDruAKohA

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("life-agrees", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "life-agrees-github"), -- change this too (tagname)
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
