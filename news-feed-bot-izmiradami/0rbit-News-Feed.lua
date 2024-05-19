-- ao.id  phLPz9diGRSL4OGhp0WkYv6Biq6vd8qj8etTZTbB-Q4

local json = require("json")
local _0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
local URL = "https://api.theblockbeats.news/v1/open-api/open-flash?size=5&page=1&type=push"
ReceivedData = ReceivedData or {}

Handlers.add(
    "Get-Request",
    Handlers.utils.hasMatchingTag("Action", "Sponsored-Get-Request"),
    function(msg)
         Send({
             Target = _0RBIT,
             Action = "Get-Real-Data",
             Url = URL
        })
        print("GET Request sent to the 0rbit process.")
    end
)

Handlers.add(
    "Receive-Data",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    function(msg)
        if not msg.Data then
            print("No data received.")
            return
        end

        local res = json.decode(msg.Data)

        ReceivedData1 = res.data.data
        local extractedData = {}
        for k, v in ipairs(ReceivedData1) do
                table.insert(extractedData, {
                    title = v.title,
                    description = v.content
                })
            ReceivedData = extractedData

        end
        print("Processed data: " .. json.encode(ReceivedData1))
    end
)

local function getLatestData(msg)
    local data = json.encode(ReceivedData)
    Handlers.utils.reply(data)(msg)
    print("Latest data sent: " .. data)
end

Handlers.add(
    "GetLatestData",
    Handlers.utils.hasMatchingTag("Action", "Get-Latest-Data"),
    getLatestData
)

local function fetchNewsPeriodically()
     Send({
         Target = _0RBIT,
         Action = "Get-Real-Data",
         Url = URL
     })
    print("Periodic GET Request sent to the 0rbit process.")
end

Handlers.add(
    "CronTick",
    Handlers.utils.hasMatchingTag("Action", "Cron"),
    fetchNewsPeriodically
)
