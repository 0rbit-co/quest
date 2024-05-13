local json = require("json")

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
-- _0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"

-- URL = "https://api.polygon.io/v3/reference/tickers/AAPL?apiKey=LN8bb9eXVfj5etsCAZpV87QA0B1hppjT"
URL = "https://saurav.tech/NewsAPI/top-headlines/category/health/in.json"

NEWS = NEWS or {}

local function fetchNews()
    Send({
        Target = _0RBIT,
        Action = "Get-Real-Data",
        Url = URL,
    })
    print(Colors.green .. "GET Request " .. URL .. " sent to the 0rbit process." .. Colors.reset)
end

local function receiveData(msg)
    print("data received...")
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

local function getNews(msg)
    local news = json.encode(NEWS)
    Handlers.utils.reply(news)(msg)
end

Handlers.add(
    "GetNews",
    Handlers.utils.hasMatchingTag("Action", "Get-News"),
    getNews
)

Handlers.add(
    "CronTick",
    Handlers.utils.hasMatchingTag("Action", "Cron"),
    fetchNews
)

Handlers.add(
    "ReceiveData",
    Handlers.utils.hasMatchingTag("Action", "Receive-Response"),
    receiveData
)
