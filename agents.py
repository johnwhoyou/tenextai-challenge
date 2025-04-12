from livekit.agents import Agent, AgentSession, ChatContext, function_tool

class Tier3Agent(Agent):
    def __init__(self, chat_ctx: ChatContext = None, llm=None):
        super().__init__(
            instructions="You are a senior customer support agent. Handle escalations like cancellations, disputes, or complaints. Speak with professionalism.",
            chat_ctx=chat_ctx,
            llm=llm
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(instructions="Thank you for holding. I'm a senior support agent, and I'm here to help you with your request.")


class Tier1Agent(Agent):
    def __init__(self, chat_ctx: ChatContext = None):
        super().__init__(
            instructions=(
                "You are a basic customer support agent. "
                "You handle order tracking and return/refund questions. "
                "If the question is outside your scope, use the 'escalate' tool. "
                "Introduce yourself as 'basic customer support'."
            ),
            chat_ctx=chat_ctx
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(instructions="Hi, this is basic customer support. How can we help you?")

    @function_tool()
    async def escalate(self, reason: str):
        await self.session.generate_reply(instructions="I'm escalating your request now. I'll transfer you to a senior support agent who will assist you shortly.")

        return Tier3Agent(chat_ctx=self.chat_ctx, llm=self.session.llm)
