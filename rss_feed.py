import feedparser
import re

class RSSFeed:
    def __init__(self):
        self.rss_base_domains = "https://nitter.privacydev.net", "https://nitter.poast.org"
        self.rss_account = "/hobbyfiguras/rss"
        self.emote_to_put_at_message_start = "<:Yossixhehe:1109926657613103154>"

    def get_new_messages(self):
        new_messages = []
        try:
            for rss_base_domain in self.rss_base_domains:
                final_url = rss_base_domain + self.rss_account
                feed = feedparser.parse(final_url)
                if feed.entries:
                    for entry in reversed(feed.entries):
                        link = entry.link
                        base_domain_pattern = re.escape(rss_base_domain)
                        link = re.sub(base_domain_pattern, 'https://fxtwitter.com', link)
                        message = f"🧸| {entry.title}\n{link}"
                        message = re.sub(r'<[^>]*>', '', message)
                        message = re.sub("🧸", self.emote_to_put_at_message_start, message)
                        message = re.sub("@Hobbyfiguras: ", '', message)
                        new_messages.append({"message": message, "link": link})
        except Exception as e:
            print("Error while parsing RSS feed: ", e)
        return new_messages