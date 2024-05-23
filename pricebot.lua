-- PID: St_egjFqHGrFxufWXxyPh_V2vgAGcUFnGDr3eokbTjo
-- IDE: https://ide.betteridea.dev/?getcode=St_egjFqHGrFxufWXxyPh_V2vgAGcUFnGDr3eokbTjo

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add("0xachraf",
    Handlers.utils.hasMatchingTag("Action", "0x-achraf"),
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
