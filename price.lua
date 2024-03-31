-- PID: VzxLJ2vBm6kkxucF0P5AJ5Nc3WGEn48nt0RMgPoOIZQ
-- IDE: https://ide.betteridea.dev/?getcode=VzxLJ2vBm6kkxucF0P5AJ5Nc3WGEn48nt0RMgPoOIZQ

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("nsikakudo", -- change this (username)
    Handlers.utils.hasMatchingTag("Action", "nsikakudo-github"), -- change this too (tagname)
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
