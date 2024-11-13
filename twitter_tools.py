from typing import Literal, Optional
from twikit import Client, Tweet, User
import asyncio
import json
import os


class PostTweetTool:
    def __init__(self, username: str, password: str):
        """Initialize Twitter client with credentials"""
        self.client = Client()
        self.username = username
        self.password = password
        self.cookies_file = "cookies.json"

    async def _load_cookies(self) -> bool:
        """Load cookies from file if they exist"""
        try:
            if os.path.exists(self.cookies_file):
                self.client.load_cookies(self.cookies_file)
                # with open(self.cookies_file, "r") as f:
                #     cookies = json.load(f)
                #     self.client.cookies = cookies
                #     self._logged_in = True
                print("Successfully logged in using cookies!")
                return True
        except Exception as e:
            print(f"Cookie loading failed: {str(e)}")
        return False

    async def _save_cookies(self):
        """Save cookies to file after successful login"""
        try:
            # Get cookies directly from the client property
            cookies = self.client.get_cookies()
            with open(self.cookies_file, "w") as f:
                json.dump(cookies, f)
            print("Cookies saved successfully!")
        except Exception as e:
            print(f"Failed to save cookies: {str(e)}")

    async def _ensure_login(self):
        """Ensure user is logged in before posting"""

        # Try loading cookies first
        if not await self._load_cookies():
            try:
                # If cookies don't work, do regular login
                await self.client.login(
                    auth_info_1=self.username, password=self.password
                )
                # Save cookies after successful login
                await self._save_cookies()
                print("Successfully logged in with credentials!")
            except Exception as e:
                return f"Login failed: {str(e)}"

    async def post_tweet(self, message: str) -> str:
        """
        Post a tweet with the given message
        Args:
            message (str): The message to tweet
        Returns:
            str: Success or error message
        """
        try:
            await self._ensure_login()
            response = await self.client.create_tweet(text=message)
            print(response)
            return "Tweet posted successfully!"
        except Exception as e:
            print(f"An error occurred while posting a tweet: {(e)}")
            return None

    async def get_tweet_by_id(self, tweet_id: str) -> Optional[Tweet]:
        """
        Get a single tweet by its ID
        Args:
            tweet_id (str): The ID of the tweet to retrieve
        Returns:
            Optional[Tweet]: The tweet object if successful, None if an error occurs
        """
        try:
            await self._ensure_login()
            tweet = await self.client.get_tweet_by_id(tweet_id)
            print("tweet", tweet)
            return tweet
        except Exception as e:
            print(f"Error retrieving tweet: {str(e)}")
            return None

    async def get_user_tweets(
        self,
        screen_name: str,
        tweet_type: Literal["Tweets", "Replies", "Media", "Likes"],
        count: int = 40,
    ) -> list[Tweet]:
        """
        Get tweets of a user
        Args:
            screen_name: Screen name of the user to retrieve tweets from
            tweet_type: Type of tweets to retrieve
            count: Number of tweets to retrieve (default: 40)
        Returns:
            list[Tweet]: List of retrieved tweets, empty list if an error occurs
        """
        try:
            await self._ensure_login()
            user = await self.client.get_user_by_screen_name(screen_name)
            tweets = await self.client.get_user_tweets(user.id, tweet_type, count)
            # Filter out retweets
            original_tweets = [
                tweet for tweet in tweets if not tweet.full_text.startswith("RT @")
            ]
            # for tweet in original_tweets:
            #     print(tweet.text)
            return original_tweets
        except Exception as e:
            print(f"Error retrieving tweets: {str(e)}")
            return []

    async def get_latest_tweet(
        self, user_id: str, tweet_type: Literal["Tweets", "Replies", "Media", "Likes"]
    ) -> Tweet:
        """Get the latest tweet of a user"""
        try:
            await self._ensure_login()
            tweet = await self.client.get_user_tweets(user_id, tweet_type)
            print(tweet)
            return tweet
        except Exception as e:
            print(f"Error retrieving latest tweet: {str(e)}")
            return None

    async def listen_for_new_tweets(
        self,
        user_id: str,
        tweet_type: Literal["Tweets", "Replies", "Media", "Likes"],
    ):
        """Listen for new tweets of a user"""
        CHECK_INTERVAL = 60 * 5  # 5 minutes
        try:
            await self._ensure_login()
            before_tweet = await self.get_latest_tweet(user_id, tweet_type)
            while True:
                await asyncio.sleep(CHECK_INTERVAL)
                latest_tweet = await self.get_latest_tweet(user_id, tweet_type)
                if (
                    before_tweet != latest_tweet
                    and before_tweet.created_at_datetime
                    < latest_tweet.created_at_datetime
                ):
                    callable(latest_tweet)
                before_tweet = latest_tweet
        except Exception as e:
            print(f"Error listening for new tweets: {str(e)}")
            return []

    async def follow_user_by_username(self, username: str) -> str:
        """
        Follow a user
        Args:
            username (str): The username of the user to follow
        Returns:
            str: Success or error message
        """
        try:
            await self._ensure_login()
            user = await self.client.get_user_by_screen_name(username)
            response = await self.client.follow_user(user.id)
            print(response)
            return "User followed successfully!"
        except Exception as e:
            print(f"An error occurred while following a user: {(e)}")
            return None

    async def reply_to_tweet(self, tweet_id: str, message: str) -> str:
        """Reply to a tweet"""
        try:
            await self._ensure_login()
            response = await self.client.create_tweet(text=message, reply_to=tweet_id)
            print(response)
            return "Tweet replied to successfully!"
        except Exception as e:
            print(f"An error occurred while replying to a tweet: {(e)}")
            return None
