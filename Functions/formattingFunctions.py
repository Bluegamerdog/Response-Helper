import discord
import requests

BasiccommandCOL = 0xFFFFFF
TRUCommandCOL = 0x8e0000
HRCommandsCOL = 0x000000
ErrorCOL = 0xB3202C
DarkRedCOL = 0x8B0000
SuccessCOL = 0x4BB543
DarkGreenCOL = 0x006400
YellowCOL = 0xb89715

def embedBuilder(embedType: str, embedDesc: str, embedTitle: str):

    match embedType:
        case "Error":
            embed = discord.Embed(
                title=embedTitle,
                description=embedDesc,
                color=ErrorCOL
            )
            embed.set_footer(text="TRU Helper In-Dev")
            #embed.set_footer(response.json()["name"])
            return embed

        case "Success":
            embed = discord.Embed(
                title=embedTitle,
                description=embedDesc,
                color=SuccessCOL
            )
            #response = requests.get("https://api.github.com/Bluegamerdog/TRU-Helper-InDev")
            #embed.set_footer(response.json()["name"])
            embed.set_footer(text="TRU Helper In-Dev")
            return embed

        case "Warning":
            embed = discord.Embed(
                title=embedTitle,
                description=embedDesc,
                color=SuccessCOL
            )
            #response = requests.get("https://api.github.com/Bluegamerdog/TRU-Helper-InDev")
            #embed.set_footer(response.json()["name"])
            embed.set_footer(text="TRU Helper In-Dev")
            return embed
        case other:
            print("No valid Embed Type passed.")


