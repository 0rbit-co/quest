-- ao.id  _ZUedzqmP-q9kqJHkGu2B1QTKcNwQGI6YJ-S6ZvO6zY

local json = require("json")

-- 0rbit process and token details
local _0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
local _0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"

-- News API URL and fee amount
local URL = "https://api.theblockbeats.news/v1/open-api/open-flash?size=5&page=1&type=push"
local FEE_AMOUNT = "1000000000000" -- 1 $0RBT

ReceivedData = ReceivedData or {}

-- Handler to send GET request to the `0rbit` process
Handlers.add(
    "Get-Request",
    Handlers.utils.hasMatchingTag("Action", "Sponsored-Get-Request"),
    function(msg)
        -- Send({
        --     Target = _0RBIT,
        --     Action = "Get-Real-Data",
        --     Url = URL
        -- })

        Send({
            Target = _0RBT_TOKEN,
            Action = "Transfer",
            Recipient = _0RBIT,
            Quantity = FEE_AMOUNT,
            ["X-Url"] = URL,
            ["X-Action"] = "Get-Real-Data"
        })
        print("GET Request sent to the 0rbit process.")
    end
)

-- Handler to receive the data from the `0rbit` process
Handlers.add(
    "Receive-Data",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    function(msg)
        if not msg.Data then
            print("No data received.")
            return
        end

        -- Attempt to decode JSON and print errors if any
        local res = json.decode(msg.Data)

        ReceivedData1 = res.data.data
        local extractedData = {}
        for k, v in ipairs(ReceivedData1) do
                table.insert(extractedData, {
                    title = v.title,
                    description = v.content
                })
            ReceivedData = extractedData
        -- print("Processed data: " .. json.encode(ReceivedData1))

        end
        print("Processed data: " .. json.encode(ReceivedData1))
    end
)

-- Function to get the latest received data
local function getLatestData(msg)
    local data = json.encode(ReceivedData)
    Handlers.utils.reply(data)(msg)
    print("Latest data sent: " .. data)
end

-- Add handler for Get-Latest-Data to fetch latest data
Handlers.add(
    "GetLatestData",
    Handlers.utils.hasMatchingTag("Action", "Get-Latest-Data"),
    getLatestData
)


local function fetchNewsPeriodically()
    -- Send({
    --     Target = _0RBIT,
    --     Action = "Get-Real-Data",
    --     Url = URL
    -- })
    Send({
        Target = _0RBT_TOKEN,
        Action = "Transfer",
        Recipient = _0RBIT,
        Quantity = FEE_AMOUNT,
        ["X-Url"] = URL,
        ["X-Action"] = "Get-Real-Data"
    })
    print("Periodic GET Request sent to the 0rbit process.")
end

-- Add handler for periodic news fetching
Handlers.add(
    "CronTick",
    Handlers.utils.hasMatchingTag("Action", "Cron"),
    fetchNewsPeriodically
)
