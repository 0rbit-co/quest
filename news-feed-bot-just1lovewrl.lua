-- aos process:  U_GoThvB1w4GpadwjmUsJcqjGU6plbKGkvGYsphcrYw

local json = require("json")

-- processId of the 0rbit process.
_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
_0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"

-- Base URL for News API
URL = "https://saurav.tech/NewsAPI/top-headlines/category/health/in.json"
FEE_AMOUNT = "1000000000000" -- 1 $0RBT

NEWS = NEWS or {}

--[[
    Function to send the latest news.
]]
function getNews(msg)
    local news = json.encode(NEWS)
    Handlers.utils.reply(news)(msg)
end

--[[
    Function to fetch the news using the 0rbit.
]]
function fetchNews()
    Send({
        Target = _0RBT_TOKEN,
        Action = "Transfer",
        Recipient = _0RBIT,
        Quantity = FEE_AMOUNT,
        ["X-Url"] = URL,
        ["X-Action"] = "Get-Real-Data"
    })
    print(Colors.green .. "GET Request sent to the 0rbit process.")
end

--[[
    Function to update the news.
]]
function receiveData(msg)
    local res = json.decode(msg.Data);
    local articles;
    local article;
    if res.status == "ok" then
        articles = res.articles;
        for k, v in pairs(articles) do
            article =
            {
                title = v.title,
                description = v.description,
                url = v.url
            }
            table.insert(NEWS, article)
        end
        print("News Updated")
    else
        print("Error in fetching news")
    end
end

--[[
    Handlers to get latest news.
]]
Handlers.add(
    "GetNews",
    Handlers.utils.hasMatchingTag("Action", "Sponsored-Get-Request"),
    getNews
)

--[[
    CRON Handler to fetch the news using 0rbit in a defined interval.
]]
Handlers.add(
    "CronTick",
    Handlers.utils.hasMatchingTag("Action", "Cron"),
    fetchNews
)

--[[
    Handlers to receive data from the 0rbit process.
]]
Handlers.add(
    "ReceiveData",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    receiveData
)
