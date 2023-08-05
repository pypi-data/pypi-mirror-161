#!/usr/bin/env python3

import discord

async def send_embed(self, embed_dict, **kwargs):
    
    return await self.send(
        embed=discord.Embed.from_dict(embed_dict),
        **kwargs
    )

discord.abc.Messageable.send_embed = send_embed
