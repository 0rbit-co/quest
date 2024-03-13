-- Process ID: MD76snAyJJICvDt2rhhA68zIjPSIYJDKuyQ19yFiTGE

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

Handlers.add(
    "pingpong",
    Handlers.utils.hasMatchingTag("Action", "Get-Price"),
    function(msg)
        local coin_ids = ''
        for i in string.gmatch(msg.Tags.IDS, "[^,]+") do
            i = i:match("^%s*(.-)%s*$")
            coin_ids = coin_ids .. i .. '%2C'
        end

        local response = ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = 'https://api.coingecko.com/api/v3/simple/price?ids=' .. coin_ids .. '&vs_currencies=usd'
        })
        Handlers.utils.reply(response.Data)(msg)
    end
)
