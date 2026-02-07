import discord
from discord.ext import commands
from discord import app_commands
import os

# Bot setup with necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="say", description="Make the bot say something")
@app_commands.describe(
    message="The message you want the bot to send",
    mention_everyone="Mention @everyone (default: False)",
    mention_here="Mention @here (default: False)"
)
async def say(
    interaction: discord.Interaction,
    message: str,
    mention_everyone: bool = False,
    mention_here: bool = False
):
    # Check if user has permission to mention everyone/here
    if (mention_everyone or mention_here) and not interaction.user.guild_permissions.mention_everyone:
        await interaction.response.send_message("❌ You don't have permission to use @everyone or @here!", ephemeral=True)
        return
    
    # Prepare the message with mentions if requested
    final_message = message
    if mention_everyone:
        final_message = f"@everyone {final_message}"
    if mention_here:
        final_message = f"@here {final_message}"
    
    # Get attachments if any (for images)
    attachments = []
    if hasattr(interaction, 'message') and interaction.message:
        attachments = [await attachment.to_file() for attachment in interaction.message.attachments]
    
    # Send the message
    allowed_mentions = discord.AllowedMentions(everyone=mention_everyone or mention_here)
    
    try:
        await interaction.response.send_message("✅ Message sent!", ephemeral=True)
        await interaction.channel.send(
            content=final_message,
            files=attachments if attachments else None,
            allowed_mentions=allowed_mentions
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending message: {e}", ephemeral=True)

@bot.tree.command(name="create", description="Create a ticket system embed")
async def create_ticket(interaction: discord.Interaction):
    # Check if user has manage channels permission
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ You don't have permission to create ticket embeds!", ephemeral=True)
        return
    
    # Create the ticket embed
    embed = discord.Embed(
        title="🎫 Support Tickets",
        description="Need help? Click the button below to create a support ticket!\n\nOur team will assist you as soon as possible.",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📋 How it works",
        value="• Click the 'Create Ticket' button\n• A private channel will be created\n• Explain your issue to our staff\n• We'll help you resolve it!",
        inline=False
    )
    embed.set_footer(text="Support Team • We're here to help!")
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
    
    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, emoji="🎫", custom_id="create_ticket")
    async def create_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
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
                name=f"ticket-{interaction.user.name}",
                overwrites=overwrites,
                reason=f"Ticket created by {interaction.user}"
            )
            
            # Send initial message in ticket
            ticket_embed = discord.Embed(
                title="🎫 Ticket Created",
                description=f"Hello {interaction.user.mention}! Thank you for creating a ticket.\n\nPlease describe your issue and our staff will assist you shortly.",
                color=discord.Color.blue()
            )
            ticket_embed.set_footer(text="To close this ticket, a staff member will delete this channel.")
            
            close_view = CloseTicketView()
            await ticket_channel.send(f"{interaction.user.mention}", embed=ticket_embed, view=close_view)
            
            await interaction.response.send_message(f"✅ Ticket created! {ticket_channel.mention}", ephemeral=True)
        
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
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify_button")
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
