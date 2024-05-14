-- PID = QivSfFC91LF5QK-5N5fdtVPFb5cOfqmC2MuOeupxMUs
-- aos 0rbitPriceFeedRelease --cron 30-seconds

local json = require("json")

-- processId of the 0rbit process.
_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

-- Base URL for coingecko API
BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

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
    local url;
    local token_ids = "";

    for _, v in pairs(TOKEN_PRICES) do
        token_ids = token_ids .. v.coingecko_id .. ","
    end

    url = BASE_URL .. "?ids=" .. token_ids .. "&vs_currencies=usd"

    Send({
        Target = _0RBIT,
        Action = "Get-Real-Data",
        Url = url
    })
    print(Colors.green .. "GET Request sent to the 0rbit process.")
end

--[[
    Function to update the token prices in the TOKEN_PRICES table
]]
function receiveData(msg)
    local res = json.decode(msg.Data)
    for k, v in pairs(res) do
        TOKEN_PRICES[ID_TOKEN[k]].price = tonumber(v.usd)
        TOKEN_PRICES[ID_TOKEN[k]].last_update_timestamp = msg.Timestamp
    end
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
