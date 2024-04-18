import feedparser
import re
import os
from datetime import datetime
from dateutil import parser

class RSSFeed:
    def __init__(self, bot):
        self.bot = bot   
        self.rss_base_domains =  self.load_rss_base_domains() 
        self.rss_account =   os.environ.get("TARGET_ACCOUNT") + "rss"
        self.emote_to_put_at_message_start = "<:Yossixhehe:1109926657613103154>"

    def load_rss_base_domains(self):
            channel_id_env = os.environ.get("RSS_PROVIDERS")
            if channel_id_env:
                return [id.strip() for id in channel_id_env.split(",")]
            else:
                return []
    def get_new_messages(self):
        new_messages = []
        try:
            sent_links_data = self.bot.firebase_service.sent_links_ref.get()
            sent_links = [link for link in sent_links_data.values()] if sent_links_data else []
            feed_entries = self.get_feed_entries()
            if feed_entries:
                for entry in feed_entries:
                    link = entry.link
                    if link not in sent_links:
                        new_messages.append({"message": self.refine_entry(entry), "link": link})
                        self.bot.firebase_service.save_sent_link(link)
        except Exception as e:
                print("Error while parsing RSS feed: ", e)
        return new_messages
    
    def get_feed_entries(self):
        feed_entries = []
        seen_links = set() 
        for rss_base_domain in self.rss_base_domains:
            final_url = rss_base_domain + self.rss_account
            print(final_url)
            try:
                feed = feedparser.parse(final_url)
                if feed.entries:
                    for entry in feed.entries:
                        self.fix_link(entry,rss_base_domain)
                        entry.published_parsed = parser.parse(entry.published)
                        if entry.link not in seen_links:
                            feed_entries.append(entry)
                            seen_links.add(entry.link)
            except TimeoutError as e:
                print("Error while parsing RSS feed: " + final_url, e)
                    
        feed_entries.sort(key=lambda x: x.published_parsed, reverse=True)
        return feed_entries
    def fix_link(self,entry,rss_base_domain):
        link = entry.link
        base_domain_pattern = re.escape(rss_base_domain)
        link = re.sub(base_domain_pattern, 'https://fxtwitter.com', link)
        entry.link = link
    
    def refine_entry(self, entry):
        message = f"🧸| {entry.title}\n{entry.link}"
        message = re.sub(r'<[^>]*>', '', message)
        message = re.sub("🧸", self.emote_to_put_at_message_start, message)
        message = re.sub("@Hobbyfiguras: ", '', message)
        return message
    
    