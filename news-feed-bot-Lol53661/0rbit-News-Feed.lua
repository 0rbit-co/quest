-- ao.id  qKII1IXxRnyAjlFzFQuK2cNYlt3ZdRLbQ8DEMA8iqfs

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
