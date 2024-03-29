
-- PID/process ID : bdnsFXyx6B8CnrjfbgCoXEc9HlhakPyY0D0ZH14wWS4

_0RBIT = "WSXUI2JjYUldJ7CKq9wE1MGwXs-ldzlUlHOQszwQe0s" -- Ganti dengan ID proses 0rbit aktual Anda
BASE_URL = "https://api.coingecko.com/api/v3/simple/price"

-- Penanganan Kesalahan Fungsi (opsional)
function handleError(msg, errorMessage)
    ao.send({
        Target = msg.From,
        Tags = {
            Action = "Error",
            ["Message-Id"] = msg.Id,
            Error = errorMessage
        }
    })
end

-- Penanganan Permintaan Harga Token
Handlers.add(
    "GetPrice",
    Handlers.utils.hasMatchingTag("Action", "Get-Price"),
    function(msg)
        local token = msg.Tags.Token

        local url = BASE_URL .. "?ids=" .. token .. "&vs_currencies=usd"

        ao.send({
            Target = _0RBIT,
            Action = "Get-Real-Data",
            Url = url
        })

        Handlers.utils.reply("PriceFetch")(msg) -- Ubah "Response" menjadi "PriceFetch"
    end
)
