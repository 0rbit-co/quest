local json = require("json")

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
_0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"

BASE_URL = "https://api.coingecko.com/api/v3/simple/price"
FEE_AMOUNT = "1000000000000"


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
LOGS = LOGS or {}


function fetchPrice()
    local url;
    local token_ids;

    for _, v in pairs(TOKEN_PRICES) do
        token_ids = token_ids .. v.coingecko_id .. ","
    end

    url = BASE_URL .. "?ids=" .. token_ids .. "&vs_currencies=usd"

    Send({
        Target = _0RBT_TOKEN,
        Action = "Transfer",
        Recipient = _0RBIT,
        Quantity = FEE_AMOUNT,
        ["X-Url"] = url,
        ["X-Action"] = "Get-Real-Data"
    })
    print(Colors.green .. "GET Request sent to the 0rbit process.")
end


function receiveData(msg)
    local res = json.decode(msg.Data)
    for k, v in pairs(res) do
        TOKEN_PRICES[ID_TOKEN[k]].price = tonumber(v.usd)
        TOKEN_PRICES[ID_TOKEN[k]].last_update_timestamp = msg.Timestamp
    end
end


function getTokenPrice(msg)
    local token = msg.Tags.Token
    local price = TOKEN_PRICES[token].price
    if price == 0 then
        Handlers.utils.reply("Price not available!!!")(msg)
    else
        Handlers.utils.reply(tostring(price))(msg)
    end
end


Handlers.add(
    "GetTokenPrice",
    Handlers.utils.hasMatchingTag("Action", "Get-Token-Price"),
    getTokenPrice
)

Handlers.add(
    "CronTick",
    Handlers.utils.hasMatchingTag("Action", "Cron"),
    fetchPrice
)


Handlers.add(
    "ReceiveData",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    receiveData
)
