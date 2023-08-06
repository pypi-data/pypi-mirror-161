"""Class to display data."""


# __credits__ https://www.notia.ai/articles/building-an-authenticated-python-cli
# '''
# display.py
# def buildProfileLink(self, username: str) -> str:
#     return f"[bold blue][link={self.TWITTER_BASE}/
# {username}]@{username}[/link][/bold blue]"

# def buildTweetLink(self, _id: str) -> str:
#     return f"[bold blue][link={self.TWITTER_BASE}/
# twitter/status/{_id}]View Tweet[/link][/bold blue]"

# def tweetsAsTable(self, tweets: List, frequency: str) -> None:
#     tweets.sort(reverse=True, key=lambda t: t[2])
#     tweets = tweets[:10]

#     table = Table( show_header=True, box=box.ROUNDED, show_lines=True,
#         padding=(0, 1, 1, 0), border_style="yellow", caption_style="not dim")
#     table.title = f"[not italic]🍰 Your {frequency} Slice of ML 🍰[/not italic]"
#     table.caption = "Made with ❤️  by the team at [bold blue]
# [link=https://notia.ai]Notia[/link][/bold blue]"
#     table.add_column("Username 🧑", justify="center")
#     table.add_column("Tweet 🐦", justify="center",
#                       header_style="bold blue", max_width=100)
#     table.add_column("Tweet Link 🔗", justify="center")
#     table.add_column("Likes ❤️", justify="center", header_style="bold red")

#     for tweet in tweets:
#         table.add_row( self.buildProfileLink(tweet[3]), tweet[1],
#             self.buildTweetLink(tweet[0]), str(tweet[2]))

#     self._console.print(table)

# cli.py
# def login(relogin):
#     (client_id, client_secret, app_name) = prompt_api_details()

#     click.echo(f"""🔑 Your Super Secret Credentials 🔑
#         Client ID: {client_id}
#         Client Secret: {client_secret}
#         App Name: {app_name}""")

# def slice(frequency):
#     credentials = read_credentials(TWITTER_API)
#     tweets = API(credentials[0], credentials[1], TWITTER_API).query(frequency)
#     Display().tweetsAsTable(tweets, frequency)
