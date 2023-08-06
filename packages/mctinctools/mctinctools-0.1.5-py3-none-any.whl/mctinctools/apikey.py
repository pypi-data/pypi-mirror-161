"""Grab API key from user via console."""
#
# __credits__ https://www.notia.ai/articles/building-an-authenticated-python-cli
# '''

# DEVELOPER_DASHBOARD_URL = "https://developer.twitter.com/en/portal/dashboard"
# def prompt_api_details() -> Tuple[str, str, str]:
#     '''Prompt user for information.'''
#     api_prompt = Panel(
#         f"""
#             You can find your API keys :key: on your Twitter App Dashboard
#             [blue underline bold][link={DEVELOPER_DASHBOARD_URL}]
# here[/link][/blue underline bold]
#         """,
#         box=box.ROUNDED,
#     )
#     display.log_styled(api_prompt, style="yellow")
#     display.log(
#         "Paste the Client ID, Secret and App Name from your profile and hit enter: "
#     )
#     client_id = getpass.getpass(prompt="Client ID 🆔 ")
#     client_secret = getpass.getpass(prompt="Client Secret 🕵️ ")
#     app_name = input("App Name ✏️  ")
#     return (client_id, client_secret, app_name)
