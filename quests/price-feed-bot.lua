-- Process ID: ON8RTSRIPg0U__6qRMtiMhf208jsiVJh8tEk5s9Z59g

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

-- Price query API: https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd
-- Coin list API: https://api.coingecko.com/api/v3/coins/list
-- coin name: bitcoin, ethereum, binancecoin
-- API documents: https://docs.coingecko.com/v3.0.1/reference/introduction

-- Process when user query price
Handlers.add("QueryCoinPrice",
    Handlers.utils.hasMatchingTag("Action", "QueryCoinPrice"),
    function(message)
        local coin_id = message.Data
        local url = "https://api.coingecko.com/api/v3/simple/price?ids=" .. coin_id .. "&vs_currencies=usd"

        -- send a tip message
        local tipMsg = "You are query price of " .. coin_id .. ", please wait for a moment to get the result"
        ao.send({ Target = message.From, Data = tipMsg })

        -- query coin price
        ao.send({ Target = _0RBIT, Action = "Get-Real-Data", Url = url })
    end
)

-- Response the price
Handlers.add(
    "ProcessOrbitReceive",
    Handlers.utils.hasMatchingTag("Action", "Receive-data-feed"),
    function(msg)
        local json = require("json")
        local res = json.decode(msg.Data)

        for _, recipient in ipairs(Members) do
            ao.send({ Target = recipient, Data = res })
        end
    end
)

-- Usage
-- ChatRoomID = "ON8RTSRIPg0U__6qRMtiMhf208jsiVJh8tEk5s9Z59g"
-- Send({ Target = ChatRoomID, Action = "Register"})
-- Send({ Target = "ON8RTSRIPg0U__6qRMtiMhf208jsiVJh8tEk5s9Z59g", Action = "QueryCoinPrice", Data = "bitcoin" })
