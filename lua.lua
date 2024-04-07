-- PID = Ya2-YoSKv3A4nSB9k9S-zFAcZodsD3Sp0kumlnMGQJ8
_ORBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s"


function handleError(msg,errorMsg)
  ao.send({
    Target= msg.From,
    Tags = {Action= "Error",["Message-Id"]=msg.Id,Error =errorMsg}
  })
  -- code
end

Handlers.add("Zedd",
Handlers.utils.hasMatchingTag("Action","zedd-nyx"),
function(msg)
  local token = msg.Tags.Token
  local url = "https://coingecko.com/api/v3/simple/price".."?ida="..token.."&vs_currencies=usd"
  ao.send({
    Target= _ORBIT,
    Action = "Get-Real-Data",
    Url=url
  })
  Handlers.utils.reply("PriceFetch")
  {msg}
end
)

Send({Target=ao.id,Action="zedd-nyx",Token = "ethereum"})
