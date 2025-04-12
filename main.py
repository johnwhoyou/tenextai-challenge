from dotenv import load_dotenv

from openai import OpenAI
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    openai,
    noise_cancellation,
)

load_dotenv()

client = OpenAI()

# OpenAI Assisstant IDs
TIER1_ID = "asst_UiMtIdh28P0wxW9An17pENOS"
TIER3_ID = "asst_UmXpbOih4kTBPObusleagDg3"
ROUTER_ID = "asst_5Tia5g46T5goarYyZvMa529y"

class RouterAgent(Agent):
    def __init__(self):
        super().__init__(instructions="Route to the appropriate support tier.")

    # to enable mid-conversation re-routing
    # to account for situations where a customer first gets routed to Tier 1
    # then asks for tier 3 questions mid-conversation
    async def on_message(self, message: str, session: AgentSession):
        router_result = client.beta.threads.create_and_run(
            assistant_id=ROUTER_ID,
            thread={"messages": [{"role": "user", "content": message}]},
            tool_choice="router_user"
        )

        # TODO: what is this line?
        tier = router_result.required_action.submit_tool_outputs.tool_calls[0].function.arguments["tier"]

        selected_id = TIER1_ID if tier == "tier_1_2" else TIER3_ID

        reply = client.beta.threads.create_and_run(
            assistant_id=selected_id,
            thread={"messages": [{"role": "user", "content": message}]}
        )

        # TODO: what is this line?
        response_text = reply.thread.messages[-1].content[0].text.value
        await session.say(response_text)

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="ash"),
    )

    await session.start(
        room=ctx.room,
        agent=RouterAgent(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply()


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))