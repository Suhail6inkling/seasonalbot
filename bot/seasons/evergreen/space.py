import logging
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from discord import Embed
from discord.ext.commands import Cog, Context, command

from bot.bot import SeasonalBot
from bot.constants import Tokens

logger = logging.getLogger(__name__)

# NASA API base URL
BASE_URL = "https://api.nasa.gov/"

# Default Parameters:
# .apod command default request parameters
APOD_PARAMS = {
    "api_key": Tokens.nasa,
    "hd": True
}


class Space(Cog):
    """Space Cog contains commands, that show images, facts or other information about space."""

    def __init__(self, bot: SeasonalBot):
        self.bot = bot
        self.http_session = bot.http_session

    @command(name="apod")
    async def apod(self, ctx: Context, date: Optional[str] = None) -> None:
        """Get Astronomy Picture of Day from NASA API. Date is optional parameter, what formatting is YYYY-MM-DD."""
        # Make copy of parameters
        params = APOD_PARAMS.copy()
        # Parse date to params, when provided. Show error message when invalid formatting
        if date:
            try:
                params["date"] = datetime.strptime(date, "%Y-%m-%d").date().isoformat()
            except ValueError:
                await ctx.send(f"Invalid date {date}. Please make sure your date is in format YYYY-MM-DD.")
                return

        # Do request to NASA API
        result = await self.fetch_from_nasa("planetary/apod", params)

        # Create embed from result
        embed = Embed(title=f"Astronomy Picture of Day in {result['date']}", description=result["explanation"])
        embed.set_image(url=result["hdurl"])
        embed.set_footer(text="Powered by NASA API")

        await ctx.send(embed=embed)

    async def fetch_from_nasa(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch information from NASA API, return result."""
        # Generate request URL from base URL, endpoint and parsed params
        async with self.http_session.get(url=f"{BASE_URL}{endpoint}?{urlencode(params)}") as resp:
            return await resp.json()


def setup(bot: SeasonalBot) -> None:
    """Load Space Cog."""
    # Check does bot have NASA API key in .env, when not, don't load Cog and print warning
    if not Tokens.nasa:
        logger.warning("Can't find NASA API key. Not loading Space Cog.")
        return

    bot.add_cog(Space(bot))
