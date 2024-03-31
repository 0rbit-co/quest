-- PID = ByvURogt_yGokPf1Ce_iuSNyC9pxLX8jovOJjgXLiho

function handleError(msg, errorMessage)
    ao.send({
        Target = msg.From,
        Tags = {
            Action = "Error",
            ["Message-ID"] = msg.Id,
            Error = errorMessage
        }
    })
    end
    
    Handlers.add("delvinryujin",
    Handlers.utils.hasMatchingTag("Action", "delvin-ryujin"),
    function(msg)
    local token = msg.Tags.Token
    local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
    ao.send({
        Target = _ORBIT,
        Action = "Get-Real-Data",
        Url = url
    })
    Handlers.utils.reply("PriceFetch")
    (msg)
    end
    )
    