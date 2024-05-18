local json = require("json")

-- Define the ORBIT target process ID
_ORBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

-- Function to handle errors
function handleError(msg, errorMessage)
    ao.send({
        Target = msg.From,
        Tags = {
            Action = "Error",
            ["Message-id"] = msg.Id,
            Error = errorMessage
        }
    })
end

-- Handler for fetching cryptocurrency prices
Handlers.add("joks",
    Handlers.utils.hasMatchingTag("Action", "micdrop"),
    function(msg)
        local token = msg.Tags.Token
        if not token then
            handleError(msg, "Token not provided")
            return
        end

        local url = "https://api.coingecko.com/api/v3/simple/price?ids=" .. token .. "&vs_currencies=usd"
        ao.send({
            Target = _ORBIT,
            Action = "Get-Real-Data",
            Url = url
        })
        Handlers.utils.reply("PriceFetch")(msg)
    end
)

-- Handler for receiving data from the ORBIT process
Handlers.add("ReceiveData",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    function(msg)
        print("Received data: " .. msg.Data)
        local res = json.decode(msg.Data)
        local token = msg.Tags.Token
        if res[token] and res[token].usd then
            ao.send({
                Target = msg.From,
                Tags = {
                    Action = "Price-Response",
                    ["Message-id"] = msg.Id,
                    Price = res[token].usd
                }
            })
            print("Price of " .. token .. " is " .. res[token].usd)
        else
            handleError(msg, "Failed to fetch price")
        end
    end
)
