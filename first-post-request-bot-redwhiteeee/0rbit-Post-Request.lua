-- PID So4Y2Ja0vXCwqKaTULmD9JH_YjzyCangM4GO8OpgPjE

local json = require("json")
 
_0RBIT = "BaMK1dfayo75s3q1ow6AO64UDpD9SEFbeE8xYrY2fyQ"
_0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"
 
FEE_AMOUNT = "1000000000000" -- 1 $0RBT
BASE_URL = "https://g8way.0rbit.co/graphql"
-- The data body to be sent in the POST request
BODY = json.encode({
                        query = [[
                            query {
                                transactions(
                                    owners: ["vh-NTHVvlKZqRxc8LyyTNok65yQ55a_PJ1zWLb9G2JI"]
                                ) {
                                    edges {
                                        node {
                                            id
                                        }
                                    }
                                }
                            }
                        ]]
                    });
 
ReceivedData = ReceivedData or {}

Handlers.add(
    "Post-Request",
    Handlers.utils.hasMatchingTag("Action", "First-Post-Request"),
    function(msg)
        Send({
            Target = _0RBT_TOKEN,
            Action = "Transfer",
            Recipient = _0RBIT,
            Quantity = FEE_AMOUNT,
            ["X-Url"] = BASE_URL,
            ["X-Action"] = "Post-Real-Data",
            ["X-Body"] = BODY
        })
        print(Colors.green .. "You have sent a POST Request to the 0rbit process.")
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
