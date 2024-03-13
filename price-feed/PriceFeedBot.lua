_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add(
    "pingpong",
    Handlers.utils.hasMatchingTag("Action", "Get-Prices"),
    function(msg)
        coin_ids = ''
        for i in string.gmatch(msg.Tags.IDS, "[^,]+") do
            i = i:match("^%s*(.-)%s*$")
            coin_ids = coin_ids .. i .. '%2C'
        end
        print(coin_ids)
        ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = 'https://api.coingecko.com/api/v3/simple/price?ids=' .. coin_ids .. '&vs_currencies=usd'
        })
        Handlers.utils.reply(coin_ids)(msg)
    end
)