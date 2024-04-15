import feedparser
import re
from datetime import datetime

class RSSFeed:
    def __init__(self, bot):
        self.bot = bot  # Store the bot instance
        self.rss_base_domains = "https://nitter.privacydev.net", "https://nitter.poast.org"
        self.rss_account = "/hobbyfiguras/rss"
        self.emote_to_put_at_message_start = "<:Yossixhehe:1109926657613103154>"

    def get_new_messages(self):
        new_messages = []
        try:
            sent_links_data = self.bot.firebase_service.sent_links_ref.get()
            sent_links = [link for link in sent_links_data.values()] if sent_links_data else []
            all_entries = []
            for rss_base_domain in self.rss_base_domains:
                final_url = rss_base_domain + self.rss_account
                feed = feedparser.parse(final_url)
                if feed.entries:
                    all_entries.extend(feed.entries)

            all_entries.sort(key=lambda x: x.published_parsed, reverse=True)

            for entry in all_entries:
                link = entry.link
                base_domain_pattern = re.escape(rss_base_domain)
                link = re.sub(base_domain_pattern, 'https://fxtwitter.com', link)
                if link not in sent_links:
                    message = f"🧸| {entry.title}\n{link}"
                    message = re.sub(r'<[^>]*>', '', message)
                    message = re.sub("🧸", self.emote_to_put_at_message_start, message)
                    message = re.sub("@Hobbyfiguras: ", '', message)
                    new_messages.append({"message": self.refine_entry(message, rss_base_domain), "link": link})
                    self.bot.firebase_service.save_sent_link(link)
        except Exception as e:
            print("Error while parsing RSS feed: ", e)
        return new_messages

    def get_feed_entries(self):
        feed_entries = []
        for rss_base_domain in self.rss_base_domains:
            final_url = rss_base_domain + self.rss_account
            feed = feedparser.parse(final_url)
            if feed.entries:
                for entry in feed.entries:
                    link = entry.link
                    base_domain_pattern = re.escape(rss_base_domain)
                    link = re.sub(base_domain_pattern, 'https://fxtwitter.com', link)
                    entry.link = link
                feed_entries.extend(feed.entries)

        feed_entries.sort(key=lambda x: x.published_parsed, reverse=True)
        return feed_entries

    def refine_entry(self, entry):
        message = f"🧸| {entry.title}\n{entry.link}"
        message = re.sub(r'<[^>]*>', '', message)
        message = re.sub("🧸", self.emote_to_put_at_message_start, message)
        message = re.sub("@Hobbyfiguras: ", '', message)
        return message