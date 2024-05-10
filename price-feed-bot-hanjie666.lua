--aos process:  QM0gImIJwUuy49zwbXhl3YiYX9Ep_rSVprauXp8JflY
_ORBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
_USERNAME = "hanjie666"
Handlers.add(_USERNAME,
        Handlers.utils.hasMatchingTag("Action", _USERNAME),
        function(msg)
            local token = msg.Tags.Token
            local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .."&vs_currencies=usd"
            ao.send({
                Target = _ORBIT,
                Action = "Get-Real-Data",
                Url = url
            })
            Handlers.utils.reply("PriceFetch")
            (msg)
        end
)