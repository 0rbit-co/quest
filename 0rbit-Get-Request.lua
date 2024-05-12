local json = require("json")
 
_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
 
BASE_URL = "https://dummyjson.com/products"
 
ReceivedData = ReceivedData or {}

Handlers.add(
    "Get-Request",
    Handlers.utils.hasMatchingTag("Action", "Sponsored-Get-Request"),
    function(msg)
        Send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = BASE_URL
        })
        print(Colors.green .. "You have sent a GET Request to the 0rbit process.")
    end
)

Handlers.add(
    "Receive-Data",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    function(msg)
        local res = json.decode(msg.Data)
        ReceivedData = res
        print(Colors.green .. "You have received the data from the 0rbit process.")
    end
)