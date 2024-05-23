-- PID = 5RTSDCnWsa3cb-zIo9MXo2Fbr0Do-wHp3UzW43imv2c

_0RBIT ="WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"

function handleError(msg, errorMessage)
ao.send({
    Target = msg.From,
        Tags = {
                Action = "Error",
                        ["Message-Id"] =msg.Id,
                                Error =errorMessage    
                                    }
                                    })
                                    end

                                    Handlers.add("exploreh",
                                    Handlers.utils.hasMatchingTag("Action", "exploreh"),
                                    function(msg)
                                    local token = msg.Tags.Token
                                    local url = "https://api.coingecko.com/api/v3/simple/price" .. "?ids=" .. token .. "&vs_currencies=usd"
                                    ao.send({
                                        Target = _0RBIT,
                                            Action = "Get-Real-Data",
                                                Url = url
                                                })
                                                Handlers.utils.reply("PriceFetch")
                                                (msg)
                                                end
                                                )