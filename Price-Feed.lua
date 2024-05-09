local json = require("json")

-- processId of the 0rbit process.
_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
_0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"

-- Base URL for Binance API
BASE_URL = "https://data-api.binance.vision/api/v3/ticker"
FEE_AMOUNT = "1000000000000" -- 1 $0RBT

--[[
    Mapping to store the Token Details
]]
TOKEN_PRICES = TOKEN_PRICES or {
    BTC = {
        symbol = "BTC",
        price = 0,
        last_update_timestamp = 0
    },
    ETH = {
        symbol = "ETH",
        price = 0,
        last_update_timestamp = 0
    },
    SOL = {
        symbol = "SOL",
        price = 0,
        last_update_timestamp = 0
    }
}

--[[
    Function to get the price of a token
]]
function getTokenPrice(msg)
    local token = msg.Tags.Token
    local price = TOKEN_PRICES[token].price
    if price == 0 then
        Handlers.utils.reply("Price not available!!!")(msg)
    else
        Handlers.utils.reply(tostring(price))(msg)
    end
end

--[[
    Function to create a GET request on 0rbit to fetch the token prices
]]
function fetchPrice()
    for symbol, details in pairs(TOKEN_PRICES) do
        local url = BASE_URL .. "?symbol=" .. details.symbol .. "USDT&windowSize=1m&type=FULL"

        Send({
            Target = _0RBT_TOKEN,
            Action = "Transfer",
            Recipient = _0RBIT,
            Quantity = FEE_AMOUNT,
            ["X-Url"] = url,
            ["X-Action"] = "Get-Real-Data"
        })
        print(Colors.green .. "GET Request sent to the 0rbit process for " .. symbol)
    end
end

--[[
    Function to update the token prices in the TOKEN_PRICES table
]]
function receiveData(msg)
    local res = json.decode(msg.Data)
    local symbol = res.symbol:sub(1, -5)  -- Remove 'USDT' from the symbol name
    TOKEN_PRICES[symbol].price = tonumber(res.lastPrice)
    TOKEN_PRICES[symbol].last_update_timestamp = msg.Timestamp
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

--[[
    Handler to receive the data from the 0rbit process
]]
Handlers.add(
    "ReceivingData",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    receiveData
)
