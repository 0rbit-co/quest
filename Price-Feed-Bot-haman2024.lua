local json = require("json")

-- processId of the 0rbit process.
_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
_0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"

-- Base URL for coingecko API
BASE_URL = "https://api.coingecko.com/api/v3/simple/price"
FEE_AMOUNT = "1000000000000" -- 1 $0RBT

--[[
    Mapping to store the Token Details
]]
TOKEN_PRICES = TOKEN_PRICES or {
    BTC = {
        coingecko_id = "bitcoin",
        price = 0,
        last_update_timestamp = 0
    },
    ETH = {
        coingecko_id = "ethereum",
        price = 0,
        last_update_timestamp = 0
    },
    SOL = {
        coingecko_id = "solana",
        price = 0,
        last_update_timestamp = 0
    }
}
ID_TOKEN = ID_TOKEN or {
    bitcoin = "BTC",
    ethereum = "ETH",
    solana = "SOL"
}

--[[
    Function to get the price of a token
]]
function getTokenPrice(msg)
    local token = msg.Tags.Token
    print("getTokenPrice called with token: " .. token)

    local price = TOKEN_PRICES[token].price
    if price == 0 then
        Handlers.utils.reply("Price not available!!!")(msg)
        print("Price not available for token: " .. token)
    else
        Handlers.utils.reply(tostring(price))(msg)
        print("Price sent for token " .. token .. ": " .. price)
    end
end

--[[
    Function to create a GET request on 0rbit to fetch the token prices
]]
function fetchPrice()
    local url;
    local token_ids = "";

    for _, v in pairs(TOKEN_PRICES) do
        token_ids = token_ids .. v.coingecko_id .. ","
    end

    url = BASE_URL .. "?ids=" .. token_ids .. "&vs_currencies=usd"

    print("Fetching prices from URL: " .. url)

    -- Send({
    --     Target = _0RBT_TOKEN,
    --     Action = "Transfer",
    --     Recipient = _0RBIT,
    --     Quantity = FEE_AMOUNT,
    --     ["X-Url"] = url,
    --     ["X-Action"] = "Get-Real-Data"
    -- })
    ao.send({
        Target = _0RBIT,
        Action = "Get-Real-Data",
        Url = url
    })

    print(Colors.green .. "GET Request sent to the 0rbit process.")
end

--[[
    Handler to get the token price from the TOKEN_PRICES table
]]
Handlers.add(
    "GetTokenPrice",
    Handlers.utils.hasMatchingTag("Action", "Get-Token-Price"),
    getTokenPrice
)


--[[
    CRON Handler to fetch the token prices using 0rbit in a defined interval.
]]
Handlers.add(
    "CronTick",
    Handlers.utils.hasMatchingTag("Action", "Cron"),
    fetchPrice
)


Handlers.add(
    "ReceivingData",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    receiveData
)

--[[
    Handler to receive the data from the 0rbit process
]]
function receiveData(msg)
    print("ReceivingData handler invoked") -- 

    -- 
    print("Received message: " .. tostring(msg.Data))

    local status, res = pcall(function() return json.decode(msg.Data) end)
    
    if not status then
        print("Error decoding JSON: " .. res)
        return
    end
    
    print("Received data from 0rbit process:")
    print(json.encode(res)) -- 

    for k, v in pairs(res) do
        if ID_TOKEN[k] and TOKEN_PRICES[ID_TOKEN[k]] then
            TOKEN_PRICES[ID_TOKEN[k]].price = tonumber(v.usd)
            TOKEN_PRICES[ID_TOKEN[k]].last_update_timestamp = msg.Timestamp
            print("Updated price for " .. ID_TOKEN[k] .. ": " .. TOKEN_PRICES[ID_TOKEN[k]].price)
        else
            print("Unknown token: " .. k)
        end
    end
end
