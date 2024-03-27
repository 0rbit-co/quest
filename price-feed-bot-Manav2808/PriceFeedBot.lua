-- Process ID: 2yXaoxARx1vbh49nwDV3CByC77GjJ4fkhLzp_9IO8zg

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

REQUESTS = {}

Handlers.add(
    "Get Price",
    Handlers.utils.hasMatchingTag("Action", "Get-Price"),
    function(msg)
        local coin_ids = ''

        for i in string.gmatch(msg.Tags.IDS, "[^,]+") do
            i = i:match("^%s*(.-)%s*$")
            coin_ids = coin_ids .. i .. '%2C'
        end

        Send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = 'https://api.coingecko.com/api/v3/simple/price?ids=' .. coin_ids .. '&vs_currencies=usd',
        })

        table.insert(REQUESTS, msg.From)
    end
)

Handlers.add(
    "Receive Data",
    Handlers.utils.hasMatchingTag("Action", "Receive-data-feed"),
    function(msg)
        ao.send({
            Target = REQUESTS[0],
            Data = Inbox[#Inbox].Data
        })
        table.remove(REQUESTS, 0)
    end
)
