Dear  livekit support our VoiceAgentPipeline currently looks like this:
STT (deepgram) -> LLM (openai assistant with gpt-4o-mini) -> TTS (openai whisper)

Normally our pipeline is working ok but our main issue is the latency .
Because of passing pdf files to our assistants we end up with slower inference timing therefore we tried to fill this gap with another LLM model (gpt3.5-turbo) which is called the transition agent.
Now when calling this transition agent using the VoiceAgentPipeline's call back function( before_llm_callback   ) we do the following:
Get chat context
Pass the chat context into the transition agent and invoke it
using agent.say() we play the transition stream

Everything works up till this point but afterwards no texts or stream from our main agent .
- Another problems we have , is simply hallucinated and duplicated texts
- When trying to load an assistant into livekit which has already a vectrstore attach to it , we continuesly get a refusal message from the assistant:"Sorry i cannot do that" 


How should we address this?
