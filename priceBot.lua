_0RBIT= "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"
Handlers.add(
    "GetPrice",
    Handlers.utils.hasMatchingTag("Action", "GetPrice"),
    function (msg)
      local coin_name = msg.Data
      Send({
        Target = _0RBIT,
        Action = "Get-Real-Data",
        Url = 'https://api.coingecko.com/api/v3/simple/price?ids=' .. coin_name .. '&vs_currencies=usd'
      })
      Handlers.utils.reply(coin_name)(msg)
    end
  )