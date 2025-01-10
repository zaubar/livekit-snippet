import logging
import asyncio
import json
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai
from livekit.agents.llm.chat_context import ChatContext, ChatMessage
from livekit.plugins.openai.beta import AssistantOptions, AssistantCreateOptions, AssistantLoadOptions
import logging
import asyncio
import requests
import aiohttp_cors
from typing import Annotated
from aiohttp import web
from random import randint
from dotenv import load_dotenv

from livekit import rtc
from datetime import datetime as dt
import json 

from livekit.plugins import deepgram
from livekit.agents.pipeline.pipeline_agent import VoicePipelineAgent
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
    metrics,
)

from livekit.plugins import turn_detector

from livekit import agents, rtc
from livekit.plugins import openai, silero , elevenlabs
from livekit.plugins.elevenlabs import Voice , VoiceSettings
from livekit.agents.llm.chat_context import ChatContext, ChatMessage, ChatImage
from livekit.plugins.openai.beta import (
    AssistantCreateOptions,
    AssistantLoadOptions ,
    AssistantLLM,
    AssistantOptions,
    OnFileUploadedInfo,
)
from livekit.agents.llm import (
    ChatContext,
    ChatImage,
    ChatMessage,
    ChatRole,
    ChatContent 
)
from livekit.agents import tokenize
from livekit.agents.pipeline import VoicePipelineAgent
from typing import AsyncIterable
from livekit.agents.llm import ChatImage, ChatMessage
from livekit.plugins.openai.beta.assistant_llm import AssistantLLM
from livekit.agents.voice_assistant import VoiceAssistant
import httpx
import re

async def entrypoint(ctx: JobContext):
    # Initialize chat contexts
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by Zaubar Company. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation."
            "You will only talk about the image you see and articles you know , nothing must be explained out of the scope of your context"
        )
        )
    
    transition_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a transition voice assistant created by Zaubar Company. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation."
            "You will only talk about the image you see and articles you know , nothing must be explained out of the scope of your context"
        )
    )

    # Connect to the LiveKit room
    await ctx.connect()

    # Wait for a participant to join
    participant = await ctx.wait_for_participant()

    # Define the transition agent with gpt-3.5-turbo
    transition_agent = openai.LLM(model="gpt-3.5-turbo")


    async def before_llm_cb(agent:VoicePipelineAgent,chat_ctx=llm.ChatContext):
        logging.debug("Transition agent is going to talk")
        transition_stream =transition_agent.chat(chat_ctx=chat_ctx)
        collected_content = []
        async for chat_chunk in transition_stream:
            # Extract the content from each chunk
            for choice in chat_chunk.choices:
                if choice.delta.content:
                    collected_content.append(choice.delta.content)

        # Combine the collected content into a single string
        resulting_string = ''.join(collected_content)

        logging.info(f"Result of the stream to string is :{resulting_string}")


        await agent.say(resulting_string,allow_interruptions=True,add_to_chat_ctx=False)
        logging.debug("Transition agent is done talking")


    # Define the primary voice agent with specified plugins
    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        before_llm_cb=before_llm_cb
    )

    # Start the agent
    agent.start(ctx.room, participant)

    # Greet the user
    await agent.say("Hello! How can I assist you today?", allow_interruptions=False,add_to_chat_ctx=True)





if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))