import openai
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from pytube import extract
from src import prompts


class ClickbaitVideo:
    """
    A class that represents a clickbaity YouTube video that can use GPT-3 to generate the question
    that arises from the video title and an answer to that question based on the video transcript.

    Attributes:
        yt_url (str):    The YouTube video URL
        api_key (str):   An OpenAI API key for the GPT-3 model
        video_id (str):  The YouTube video ID
        title (str):     The title of the YouTube video
        transcript(str): A transcript of the video based on human- or autogenerated subtitles
        question(str):   A GPT3-powered transformation of the video title into a question
        answer_model_type(str): The model type to be used for answering, either 'text-curie-001' or 'text-davinci-003'
    """

    def __init__(
        self,
        yt_url: str,
        api_key: str,
        question_model: str = "text-davinci-003",
        answer_model_type: str = "text-curie-001",
    ):
        self.yt_url = yt_url
        self.api_key = api_key
        self.question_model = question_model
        self.answer_model_type = answer_model_type

        self.video_id = extract.video_id(self.yt_url)
        self.title = self._fetch_title()
        self.transcript = self._get_transcript()
        self.question = self._generate_question_from_title()

    def answer_title_question(self) -> str:
        """
        Generates an answer to the current question using OpenAI's GPT-3 language model.

        Returns:
            str: A string containing the answer to the current question.

        Raises:
            openai.error.OpenAIError: If there is an error while communicating with the OpenAI API.
        """

        completion = openai.Completion.create(
            model=self.answer_model_type,
            prompt=prompts.answer_question_prompt(self.transcript, self.question),
            max_tokens=100,
        )

        return completion.choices[0].text

    def _generate_question_from_title(self, gpt_model="text-davinci-003") -> str:
        """
        Generates a question impliedby the video title using OpenAI's GPT-3 language model.

        Returns:
            str: A string containing the question.

        Raises:
            openai.error.OpenAIError: If there is an error while communicating with the OpenAI API.
        """
        completion = openai.Completion.create(
            model=gpt_model,
            prompt=prompts.question_from_title_prompt(self.title),
            max_tokens=200,
        )

        return completion.choices[0].text

    def _fetch_title(self) -> str:
        """
        Fetches the title of a YouTube video using the YouTube API.

        Returns:
            str: A string containing the title of the video.
        """

        response = requests.get(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={self.video_id}&format=json"
        )
        data = response.json()
        return data["title"]

    def _get_transcript(self) -> str:
        """
        Retrieves the transcript for a YouTube video using the YouTubeTranscriptApi package.

        Returns:
            str: A string containing the formatted transcript of the video.
        """
        transcript = YouTubeTranscriptApi.get_transcript(self.video_id)
        return TextFormatter().format_transcript(transcript).replace("\n", " ")
