--[[
    (BEFORE YOU READ THE REST, I WANTED TO TELL YOU THAT JESUS LOVES YOU)
    EasyLua is a script made to help new roblox exploiters, providing them with functions like DownloadImage, comments that guide them through the script.

    How to use this script?

    local API = loadstring(game:HttpGet(ScriptUrl))()

    And then you can use the API's functions like you see them.
    Made by ballsman3761 on discord.
]]

--* Services

local HttpService = game:GetService("HttpService")

--^ Variables (Localization for performance, because using string.find multiple times is slower than doing local v1 = string.find and using v1):

local string, table, task, Instance, game, debug = string, table, task, Instance, workspace.Parent, debug

local find, gsub, sub, rep, format, match, gmatch, split, byte, char, lower, upper = string.find, string.gsub, string.sub, string.rep, string.format, string.match, string.gmatch, string.split, string.byte, string.char, string.lower, string.upper
local tfind, tinsert, tconcat, tunpack, tclear = table.find, table.insert, table.concat, table.unpack, table.clear

local Instance_new = Instance.new

local UDim2_fromOffset = UDim2.fromOffset
local deg, sqrt, atan2, random, clamp = math.deg, math.sqrt, math.atan2, math.random, math.clamp

--& Lua(u) Globals

local pcall, next, tostring, tonumber, assert, typeof, tick, setfenv, getfenv, setmetatable, error, newproxy = pcall, next, tostring, tonumber, assert, typeof, tick, setfenv, getfenv, setmetatable, error, newproxy
local wait, spawn, delay = task.wait, task.spawn, task.delay

local API = {
    Version = "1.0.0"
}

local Request = (syn and syn.request or fluxus and fluxus.request or http and http.request or request or function(Args) -- HTTP Request function for low level executors.
        -- Args: {Url: string, Method: string, Headers: table | nil, Body: string | nil}
        Args = Args or {};
        local Url, Method, Headers, Body = Args.Url, Args.Method, Args.Headers, Args.Body

        --! Assertions
        assert(Url, "Missing request url.")
        assert(Method, "Missing request method.")

        --* Main Function

        local Content = {}

        HttpService:RequestInternal({
            Url = Url,
            Method = Method,
            Headers = Headers,
            Body = Body
        }):Start(function(Success, Returned)
            Content = Returned
            Content.Success = Success
        end)

        repeat
            wait()
        until
            Content.Success ~= nil

        return Content;
    end)

function API:DownloadImage(Url, SaveAs) -- Url is the image you want to download, for example, https://cdn.discordapp.com/avatars/..., SaveAs is the file you want to save it as.
    assert(typeof(Url) == "string", "Invalid argument #1 to DownloadImage, string expected got \"" .. tostring(Url) .. "\"")
    assert(typeof(SaveAs) == "string", "Invalid argument #2 to DownloadImage, string expected got \"" .. tostring(SaveAs) .. "\"")

    writefile(SaveAs, Request({
        Url = Url,
        Method = "GET"
    }).Body) -- Basically, this makes a file with the name being SaveAs's value, And the content being the content of the url given.

    return SaveAs -- Returns the path of the image. (SaveAs)
end

function API:GetImage(Type, Data)
    --[[
        When Type is Url, it will send a GET request to the second parameter and use the content of it,
        When Type is File, it will read the file and use it's content.

        Extra Note:

        I believe the only supported image types as of 18th of february 2025 are .png, .jpg, .ico is unsupported, i don't know about the rest.
    ]]

    assert(typeof(Type) == "string", "Invalid argument #1 to GetImage, string expected got " .. tostring(Type))
    assert(typeof(Data) == "string", "Invalid argument #2 to GetImage, string expected got " .. tostring(Data))

    local File;
    local temp_file_name = HttpService:GenerateGUID(false)
    local use_files = lower(Type) ~= "url"

    File = not use_files and API:DownloadImage(Data, temp_file_name) or Data

    assert(isfile(File), "No file with the path \"" .. File .. "\" found.")

    if not use_files then
        delay(3, function()
            delfile(temp_file_name) -- Delete the file we just created because it's still cached and we can use the image, deleting it gives the user less storage usage & less flooding of their workspace folder.
        end)
    end

    return getcustomasset(File)
end

function API:CreateBridge(Handler)
    --[[
        Okay, this is a little complex for new scripters so i'll try my best to explain it:

        This function creates a bridge, basically something you can GET and POST data from & to, How it works is:

        local Bridge = API:CreateBridge(function(Path, ...) print("Bridge received request, path:",Path,"extra arguments:",...) end)

        This, whenever the Bridge object you created gets a sent a request, Will print what path the request was sent to, and the arguments it had.

        This can be useful for creating memory efficent scripts, like:

        local Bridge = API:CreateBridge(...)

        game.Players.PlayerAdded:Connect(function(plr)
            Bridge:Post("/main", {
                Event = "PlayerAdded",
                Player = plr
            })
        end)

        This can be used for fancy transferring of data across your script, and pretty cool to use.

        To stop the bridge, You're given a key to protect other functions from disabling the bridge, You're given a 128 character long key, and only that key can be used to stop the bridge,

        Syntax:

        local Bridge, Key = ...
        Bridge:Stop(Key)

        If you do:

        Bridge:Stop("hi")

        It will not work, because hi isnt equal to the Key.
    ]]

    local Generated = ""
    local addr = match(tostring(function()end), "0x.+")

    for _ = 1, 4 do Generated = Generated .. HttpService:GenerateGUID(random(1,2) == 2) end

    local Object = newproxy(true)
    
    local Event = Instance_new("BindableEvent")
    
    local Connections = {}
    local Connection;

    Connection = Event.Event:Connect(Handler)

    local mt = {
        __index = {
            Post = function(_, ...)
                return Event:Fire(...)
            end,
            Stop = function(_, ValidationKey)
                if ValidationKey == Generated then
                    Connection:Disconnect()

                    for _, C in next, Connections do
                        C:Disconnect()
                    end

                    tclear(Connections)
                end
            end
        },
        __tostring = function()
            return "Bridge: " .. addr
        end,
        __metatable = "This metatable is protected."
    }

    getmetatable(Object).__index = mt.__index
    getmetatable(Object).__newindex = mt.__newindex
    getmetatable(Object).__tostring = mt.__tostring

    return Object, Generated
end

return API
