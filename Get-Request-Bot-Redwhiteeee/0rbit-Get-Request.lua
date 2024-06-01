-- PID So4Y2Ja0vXCwqKaTULmD9JH_YjzyCangM4GO8OpgPjE

local json = require("json")
 
_0RBIT = "BaMK1dfayo75s3q1ow6AO64UDpD9SEFbeE8xYrY2fyQ"
_0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"
 
FEE_AMOUNT = "1000000000000" -- 1 $0RBT
BASE_URL = "https://dummyjson.com/products"
 
ReceivedData = ReceivedData or {}

Handlers.add(
    "Get-Request",
    Handlers.utils.hasMatchingTag("Action", "First-Get-Request"),
    function(msg)
        Send({
            Target = _0RBT_TOKEN,
            Action = "Transfer",
            Recipient = _0RBIT,
            Quantity = FEE_AMOUNT,
            ["X-Url"] = BASE_URL,
            ["X-Action"] = "Get-Real-Data"
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
