import discord
from discord.ext import commands
from discord import app_commands
import os
from collections import defaultdict

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.invites = True  # Required for invite tracking

bot = commands.Bot(command_prefix="!", intents=intents)

# Store invite data
invite_cache = {}  # {guild_id: {code: invite_object}}
invite_uses = defaultdict(lambda: defaultdict(int))  # {guild_id: {user_id: invite_count}}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    # Cache all invites for invite tracking
    for guild in bot.guilds:
        try:
            invites = await guild.invites()
            invite_cache[guild.id] = {invite.code: invite for invite in invites}
            print(f"Cached {len(invites)} invites for {guild.name}")
        except discord.Forbidden:
            print(f"Missing permissions to fetch invites in {guild.name}")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_member_join(member):
    """Track which invite was used when a member joins"""
    try:
        # Get current invites
        invites_after = await member.guild.invites()
        invites_before = invite_cache.get(member.guild.id, {})
        
        # Find which invite was used
        used_invite = None
        for invite in invites_after:
            before = invites_before.get(invite.code)
            if before and invite.uses > before.uses:
                used_invite = invite
                break
        
        # Update cache
        invite_cache[member.guild.id] = {invite.code: invite for invite in invites_after}
        
        # Send welcome message with invite info
        if used_invite:
            inviter = used_invite.inviter
            invite_uses[member.guild.id][inviter.id] += 1
            
            # Try to find a welcome channel (customize this as needed)
            welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome") or \
                             discord.utils.get(member.guild.text_channels, name="general") or \
                             member.guild.system_channel
            
            if welcome_channel:
                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=f"Welcome {member.mention} to **{member.guild.name}**!",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="📨 Invited by",
                    value=f"{inviter.mention} ({inviter.name}#{inviter.discriminator})",
                    inline=True
                )
                embed.add_field(
                    name="📊 Inviter Stats",
                    value=f"Total invites: **{invite_uses[member.guild.id][inviter.id]}**",
                    inline=True
                )
                embed.add_field(
                    name="👥 Member Count",
                    value=f"You are member #{member.guild.member_count}",
                    inline=False
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"Account created: {member.created_at.strftime('%Y-%m-%d')}")
                
                await welcome_channel.send(embed=embed)
        else:
            # Couldn't determine which invite was used
            welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome") or \
                             discord.utils.get(member.guild.text_channels, name="general") or \
                             member.guild.system_channel
            
            if welcome_channel:
                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=f"Welcome {member.mention} to **{member.guild.name}**!",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="👥 Member Count",
                    value=f"You are member #{member.guild.member_count}",
                    inline=False
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                
                await welcome_channel.send(embed=embed)
    
    except Exception as e:
        print(f"Error tracking invite: {e}")

@bot.event
async def on_invite_create(invite):
    """Update cache when a new invite is created"""
    if invite.guild.id not in invite_cache:
        invite_cache[invite.guild.id] = {}
    invite_cache[invite.guild.id][invite.code] = invite

@bot.event
async def on_invite_delete(invite):
    """Update cache when an invite is deleted"""
    if invite.guild.id in invite_cache:
        invite_cache[invite.guild.id].pop(invite.code, None)

@bot.tree.command(name="say", description="Make the bot say something")
@app_commands.describe(
    message="The message you want the bot to send (use @everyone or @here in your text where you want them)"
)
async def say(
    interaction: discord.Interaction,
    message: str
):
    # Check if user has permission to mention everyone/here if they're using these mentions
    has_everyone = "@everyone" in message or "@here" in message
    
    if has_everyone and not interaction.user.guild_permissions.mention_everyone:
        await interaction.response.send_message("❌ You don't have permission to use @everyone or @here!", ephemeral=True)
        return
    
    # Send the message with mentions enabled if they're present
    allowed_mentions = discord.AllowedMentions(everyone=has_everyone)
    
    try:
        await interaction.response.send_message("✅ Message sent!", ephemeral=True)
        await interaction.channel.send(
            content=message,
            allowed_mentions=allowed_mentions
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending message: {e}", ephemeral=True)

# Ban command (!bl)
@bot.command(name="bl")
@commands.has_permissions(ban_members=True)
async def ban_user(ctx, user_id: int, *, reason: str = "No reason provided"):
    """Ban a user by their ID"""
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.ban(user, reason=reason)
        
        embed = discord.Embed(
            title="🔨 User Banned",
            description=f"Banned **{user.name}#{user.discriminator}**",
            color=discord.Color.red()
        )
        embed.add_field(name="User ID", value=user_id, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Banned by {ctx.author.name}")
        
        await ctx.send(embed=embed)
    except discord.NotFound:
        await ctx.send("❌ User not found!")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this user!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@ban_user.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to ban members!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!bl <user_id> [reason]`")

# Unban command (!unbl)
@bot.command(name="unbl")
@commands.has_permissions(ban_members=True)
async def unban_user(ctx, user_id: int):
    """Unban a user by their ID"""
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        
        embed = discord.Embed(
            title="✅ User Unbanned",
            description=f"Unbanned **{user.name}#{user.discriminator}**",
            color=discord.Color.green()
        )
        embed.add_field(name="User ID", value=user_id, inline=True)
        embed.set_footer(text=f"Unbanned by {ctx.author.name}")
        
        await ctx.send(embed=embed)
    except discord.NotFound:
        await ctx.send("❌ User not found or not banned!")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unban users!")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@unban_user.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to unban members!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Usage: `!unbl <user_id>`")

# Invite tracking commands
@bot.command(name="invites")
async def check_invites(ctx, member: discord.Member = None):
    """Check how many people someone invited"""
    member = member or ctx.author
    
    invite_count = invite_uses[ctx.guild.id][member.id]
    
    embed = discord.Embed(
        title="📊 Invite Statistics",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name=f"{member.name}#{member.discriminator}",
        value=f"Total invites: **{invite_count}**",
        inline=False
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name="leaderboard", aliases=["lb", "top"])
async def invite_leaderboard(ctx):
    """Show the invite leaderboard"""
    guild_invites = invite_uses[ctx.guild.id]
    
    if not guild_invites:
        await ctx.send("❌ No invite data available yet!")
        return
    
    # Sort by invite count
    sorted_invites = sorted(guild_invites.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(
        title="🏆 Top Inviters",
        description=f"Leaderboard for **{ctx.guild.name}**",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (user_id, count) in enumerate(sorted_invites, 1):
        member = ctx.guild.get_member(user_id)
        if member:
            medal = medals[i-1] if i <= 3 else f"**{i}.**"
            embed.add_field(
                name=f"{medal} {member.name}#{member.discriminator}",
                value=f"Invites: **{count}**",
                inline=False
            )
    
    embed.set_footer(text=f"Total tracked invites: {sum(guild_invites.values())}")
    
    await ctx.send(embed=embed)

@bot.command(name="resetinvites")
@commands.has_permissions(administrator=True)
async def reset_invites(ctx, member: discord.Member = None):
    """Reset invite count for a member or all members"""
    if member:
        invite_uses[ctx.guild.id][member.id] = 0
        await ctx.send(f"✅ Reset invite count for {member.mention}")
    else:
        invite_uses[ctx.guild.id].clear()
        await ctx.send("✅ Reset all invite counts for this server!")

@reset_invites.error
async def reset_invites_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Only administrators can reset invite counts!")

@bot.tree.command(name="create", description="Create a ticket system embed")
async def create_ticket(interaction: discord.Interaction):
    # Check if user has manage channels permission
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ You don't have permission to create ticket embeds!", ephemeral=True)
        return
    
    # Create the ticket embed
    embed = discord.Embed(
        title="Qua Tickets",
        description="Need help? Click the button below to create a support ticket!\n\nOur team will assist you as soon as possible.",
        color=discord.Color(0xFFA500)
    )
    embed.add_field(
        name="How it works",
        value="• Click the 'Create Ticket' button\n• A private channel will be created\n• Explain your issue to our staff\n• We'll help you resolve it!",
        inline=False
    )
    embed.set_footer(text="Qua Support Team | We're here to help!")
    embed.set_image(url="https://media.discordapp.net/attachments/1469773664127029481/1469776982555492558/cimage.png?ex=6988e3fb&is=6987927b&hm=c0055497a095d34bbc090fbe50bea256651b3aae5ccabae445c1c6d800aa73b1&=&format=webp&quality=lossless&width=708&height=354")
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    
    # Create button view
    view = TicketView()
    
    await interaction.response.send_message("✅ Ticket embed created!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

@bot.tree.command(name="verify", description="Create a verification embed")
@app_commands.describe(role_id="The role ID to give verified members (default: 1469777067762647162)")
async def verify(interaction: discord.Interaction, role_id: str = "1469777067762647162"):
    # Check if user has manage roles permission
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ You don't have permission to create verification embeds!", ephemeral=True)
        return
    
    # Create the verification embed
    embed = discord.Embed(
        title="✅ Server Verification",
        description="Welcome to our server! Please verify yourself to gain access to all channels.",
        color=discord.Color.green()
    )
    embed.add_field(
        name="🔐 How to verify",
        value="Click the **Verify** button below to get verified and access the server!",
        inline=False
    )
    embed.add_field(
        name="📜 Rules",
        value="By verifying, you agree to follow our server rules and guidelines.",
        inline=False
    )
    embed.set_footer(text="Thank you for joining our community!")
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    
    # Create button view with the role ID
    view = VerifyView(role_id)
    
    await interaction.response.send_message("✅ Verification embed created!", ephemeral=True)
    await interaction.channel.send(embed=embed, view=view)

# Ticket Button View
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="buy", style=discord.ButtonStyle.green, emoji="🛒", custom_id="buy_ticket")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "🛒 Buy")
    
    @discord.ui.button(label="support", style=discord.ButtonStyle.blurple, emoji="🔗", custom_id="support_ticket")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "🔗 Support")
    
    @discord.ui.button(label="staff applications", style=discord.ButtonStyle.red, emoji="⭐", custom_id="staff_app_ticket")
    async def staff_app_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "⭐ Staff Application")
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        # Check if user already has an open ticket
        guild = interaction.guild
        existing_ticket = discord.utils.get(guild.channels, name=f"ticket-{interaction.user.name.lower()}")
        
        if existing_ticket:
            await interaction.response.send_message(f"❌ You already have an open ticket: {existing_ticket.mention}", ephemeral=True)
            return
        
        # Create ticket channel
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            ticket_channel = await guild.create_text_channel(
                name=f"{ticket_type[:1].lower()}-ticket-{interaction.user.name}",
                overwrites=overwrites,
                reason=f"{ticket_type} ticket created by {interaction.user}"
            )
            
            # Send initial message in ticket
            ticket_embed = discord.Embed(
                title=f"🎫 {ticket_type} Ticket Created",
                description=f"Hello {interaction.user.mention}! Thank you for creating a {ticket_type.lower()} ticket.\n\nPlease describe your request and our staff will assist you shortly.",
                color=discord.Color.blue()
            )
            
            # Set different colors based on ticket type
            if "buy" in ticket_type.lower():
                ticket_embed.color = discord.Color.green()
            elif "support" in ticket_type.lower():
                ticket_embed.color = discord.Color.blue()
            elif "staff" in ticket_type.lower():
                ticket_embed.color = discord.Color.red()
            elif "media" in ticket_type.lower():
                ticket_embed.color = discord.Color.light_grey()
            
            ticket_embed.set_footer(text="To close this ticket, a staff member will delete this channel.")
            
            close_view = CloseTicketView()
            await ticket_channel.send(f"{interaction.user.mention}", embed=ticket_embed, view=close_view)
            
            await interaction.response.send_message(f"✅ {ticket_type} ticket created! {ticket_channel.mention}", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating ticket: {e}", ephemeral=True)

# Close Ticket Button View
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user has manage channels permission
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Only staff members can close tickets!", ephemeral=True)
            return
        
        await interaction.response.send_message("🔒 Closing ticket in 3 seconds...", ephemeral=False)
        await interaction.channel.send("📋 This ticket has been closed by a staff member.")
        
        import asyncio
        await asyncio.sleep(3)
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")
        
# Verify Button View
class VerifyView(discord.ui.View):
    def __init__(self, role_id: str):
        super().__init__(timeout=None)
        self.role_id = int(role_id)
    
    @discord.ui.button(label="Click here for verification", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get the role
        role = interaction.guild.get_role(self.role_id)
        
        if not role:
            await interaction.response.send_message("❌ Verification role not found! Please contact an administrator.", ephemeral=True)
            return
        
        # Check if user already has the role
        if role in interaction.user.roles:
            await interaction.response.send_message("✅ You are already verified!", ephemeral=True)
            return
        
        # Add the role
        try:
            await interaction.user.add_roles(role, reason="Verified through verification system")
            await interaction.response.send_message(f"✅ You have been verified! You now have access to the server.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error verifying: {e}\nPlease contact an administrator.", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        print("ERROR: Please set TOKEN environment variable")
        print("For Railway: Add TOKEN in the Variables section")
    else:
        bot.run(TOKEN)
