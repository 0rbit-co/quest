-- PID = 1BzELa5c03KwsQy07IXf75fpdDz98N3hc6jtAzBr64E

local json = require("json")

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
-- _0RBT_TOKEN = "BUhZLMwQ6yZHguLtJYA5lLUa9LQzLXMXRfaq9FVcPJc"

URL = "https://saurav.tech/NewsAPI/top-headlines/category/health/in.json"
FEE_AMOUNT = "1000000000000" -- 1 $0RBT
NEWS = NEWS or {}



function fetchNews()
    Send({
        Target = _ORBIT,
        Action = "Get-Real-Data",
        Url = url
    })
    print(Colors.green .. "GET Request sent to the 0rbit process.")
end

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

function getNews(msg)
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