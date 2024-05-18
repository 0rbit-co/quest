-- PID OdbBgNPKup7cmWEXTY7gcsN97pQ1k1BuFV84_l29vE0

local json = require("json")

-- processId of the 0rbit process.
_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

-- Base URL for CoinGecko API
BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

-- Log storage
LOGS = LOGS or {}

-- Utility function to log messages
local function log_message(from, tag, data)
    table.insert(LOGS, {
        From = from,
        Tag = tag,
        Data = data
    })
end

-- Function to handle errors
local function handleError(msg, errorMessage)
    ao.send({
        Target = msg.From,
        Tags = {
            Action = "Error",
            ["Message-Id"] = msg.Id,
            Error = errorMessage
        }
    })
end

-- Handler for price fetch request
Handlers.add("GetPrice",
    Handlers.utils.hasMatchingTag("Action", "Get-Price"),
    function(msg)
        local token = msg.Tags.Token
        if not token then
            handleError(msg, "Token not provided")
            return
        end
        
        local url = BASE_URL .. "?ids=" .. token .. "&vs_currencies=usd"
        ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = url,
            Tags = { Token = token }
        })
        print("Price fetch request sent for " .. token)
    end
)

-- Handler to receive data and send the price response
Handlers.add("ReceiveData",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    function(msg)
        print("Received data: " .. msg.Data)
        local res = json.decode(msg.Data)
        local token = msg.Tags.Token
        if res and res[token] and res[token].usd then
            ao.send({
                Target = msg.From,
                Tags = {
                    Action = "Price-Response",
                    ["Message-Id"] = msg.Id,
                    Price = res[token].usd
                }
            })
            print("Price of " .. token .. " is " .. res[token].usd)
            log_message(msg.From, "ReceiveData", { Token = token, Price = res[token].usd, Timestamp = msg.Timestamp })
        else
            handleError(msg, "Failed to fetch price")
            log_message(msg.From, "ReceiveData", { Token = token, Message = "Failed to fetch price" })
        end
    end
)

-- Handler for GitHub request
Handlers.add("B0DH1i",
    Handlers.utils.hasMatchingTag("Action", "Sponsored-Get-Request"),
    function(msg)
        local token = msg.Tags.Token
        if not token then
            handleError(msg, "Token not provided")
            return
        end
        
        local url = BASE_URL .. "?ids=" .. token .. "&vs_currencies=usd"
        ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = url,
            Tags = { Token = token }
        })
        print("Price fetch request sent for " .. token)
    end
)
