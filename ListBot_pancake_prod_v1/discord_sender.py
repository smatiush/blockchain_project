'''# system library for getting the command line argument
import sys

# web library
import http.client


def send_discord_msg(message):
    # your webhook URL
    webhookurl = "https://discord.com/api/webhooks/814461371994341446/Etawop6Zb8D_j-OXFdZyKKVWVgC9mvPyQLcjw7xQ4JmLyB8Mpf6TXk9dv2Gk9HWRYLd5"#"https://discordapp.com/api/webhooks/YOURWEBHOOK"

    # compile the form data (BOUNDARY can be anything)
    formdata = message #'#"------:::BOUNDARY:::\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + message + "\r\n------:::BOUNDARY:::--"

    # get the connection and make the request
    connection = http.client.HTTPSConnection("discordapp.com")
    connection.request("POST", webhookurl, formdata, {
        'content-type': "multipart/form-data; boundary=----:::BOUNDARY:::",
        'cache-control': "no-cache",
    })

    # get the response
    response = connection.getresponse()
    result = response.read()

    # return back to the calling function with the result
    return result.decode("utf-8")

if __name__=='__main__':
    print(send_discord_msg('hello'))'''
from discord import Webhook, RequestsWebhookAdapter


def send_discord_msg(msg):
    webhook = Webhook.from_url("https://discord.com/api/webhooks/814461371994341446/Etawop6Zb8D_j-OXFdZyKKVWVgC9mvPyQLcjw7xQ4JmLyB8Mpf6TXk9dv2Gk9HWRYLd5", adapter=RequestsWebhookAdapter())
    webhook.send(str(msg))

if __name__ == '__main__':
    send_discord_msg('lol')