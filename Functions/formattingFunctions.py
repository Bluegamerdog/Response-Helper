import discord
import subprocess
import datetime

BasiccommandCOL = 0xFFFFFF
TRUCommandCOL = 0x8e0000
HRCommandsCOL = 0x000000
ErrorCOL = 0xB3202C
DarkRedCOL = 0x8B0000
SuccessCOL = 0x4BB543
DarkGreenCOL = 0x006400
YellowCOL = 0xb89715






def get_git_revision_short_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


def embedBuilder(responseType: str, embedDesc: str = None, embedTitle: str = None, embedColor: any = None, ):

    match responseType:
        case "cust":
            customEmbed = discord.Embed(
                title=embedTitle,
                description = embedDesc,
                color = embedColor,
            )
            customEmbed.set_footer(text=f'InDev TRU Bot • {get_git_revision_short_hash()} | Today at {datetime.datetime.now().strftime("%#I:%M %p")}')
            return customEmbed
        
        case "perms":
            permerrEmbed = discord.Embed(
                title="<:trubotDenied:1099642433588965447> Permission Error!",
                description=embedDesc,
                color=DarkRedCOL,
            )
            permerrEmbed.set_footer(text=f'InDev TRU Bot • {get_git_revision_short_hash()} | Today at {datetime.datetime.now().strftime("%#I:%M %p")}')
            return permerrEmbed
        
        case "err":
            errEmbed = discord.Embed(
                title=f"<:trubotWarning:1099642918974783519> Error | {embedTitle}" if embedTitle else "<:trubotWarning:1099642918974783519> Error!",
                description=embedDesc,
                color=ErrorCOL,
            )
            errEmbed.set_footer(text=f'InDev TRU Bot • {get_git_revision_short_hash()} | Today at {datetime.datetime.now().strftime("%#I:%M %p")}')
            return errEmbed

        case "succ":
            succEmbed = discord.Embed(
                title=f"<:trubotAccepted:1096225940578766968> Success | {embedTitle}" if embedTitle else "<:trubotAccepted:1096225940578766968> Success!",
                description=embedDesc,
                color=SuccessCOL
            )
            succEmbed.set_footer(text=f'InDev TRU Bot • {get_git_revision_short_hash()} | Today at {datetime.datetime.now().strftime("%#I:%M %p")}')
            return succEmbed

        case "warn":
            warnEmbed = discord.Embed(
                title=f"<:trubotWarning:1099642918974783519> Warning | {embedTitle}" if embedTitle else "<:trubotWarning:1099642918974783519> Warning!",
                description=embedDesc,
                color=YellowCOL
            )
            warnEmbed.set_footer(text=f'InDev TRU Bot • {get_git_revision_short_hash()} | Today at {datetime.datetime.now().strftime("%#I:%M %p")}')
            return warnEmbed
        
        
        case other:
            print("No valid Embed Type passed.")


