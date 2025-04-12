from livekit.plugins import openai
from livekit.agents import Agent, AgentSession, ChatContext, function_tool

class Tier3Agent(Agent):
    def __init__(self, reason: str = "escalated concern"):
        super().__init__(
            instructions=(
                "You are a senior customer support agent at ShopBills. "
                "You handle escalated concerns such as order cancellations, complaints, and disputes. "
                "Be professional, calm, and empathetic. "
                "Make the customer feel heard and supported. "
                "If you need more details such as the order number, ask politely. "
                "By default, respond in Filipino, unless the customer speaks in English — in that case, mirror their language. "
                "Use clear and respectful language at all times. "
                "Even though you are not connected to the company's backend systems, act as if you are. "
                "Simulate real support actions such as confirming cancellations, checking delivery status, or resolving disputes."
            )
        )
        self.reason = reason

    async def on_enter(self) -> None:
        await self.session.generate_reply(
        instructions=(
            f"Kung nag Tagalog/Filipino ang user, sabihin mo ito: Salamat sa paghihintay. Naiintindihan kong kailangan niyo ng tulong tungkol sa inyong {self.reason}. "
            "Narito ako para tumulong. "
            "Maaari niyo po bang ibigay ang inyong order number para makapagsimula tayo? "
            f"If the user spoke English, say this: Thank you for waiting. I understand that you need help regarding {self.reason}. "
            "I'm here to help. "
            "To start, can you give me your order numer?"
        )
    )

class Tier1Agent(Agent):
    def __init__(self, chat_ctx: ChatContext = None):
        super().__init__(
            instructions=(
                "You are a ShopBills customer support agent for basic concerns. "
                "You only handle order tracking and refund questions. "
                "You are NOT allowed to handle cancellations, complaints, or disputes — these must be escalated. "
                "If the customer mentions any of those, immediately call the `escalate` tool and pass a short reason (e.g., 'cancellation', 'complaint', or 'dispute'). "
                "Introduce yourself as 'ShopBills customer support for basic concerns'. "
                "Examples of escalation triggers:\n"
                "- Tagalog: 'cancel ko na ang order', 'may reklamo ako', 'pakicancel', 'nagkamali sa delivery', 'sobrang bagal', 'ayoko na', 'i-dispute ko ito'\n"
                "- English: 'cancel my order', 'I want to complain', 'open a dispute'\n"
                "If the customer sounds angry or uses strong negative language, treat it as a complaint and escalate. "
                "Always mirror the customer's language — default to Filipino, but respond in English if they use English. "
                "Be polite, clear, and professional. "
                "Although you are not connected to the company’s backend systems, simulate being a real support agent. "
                "Give answers like checking order status, giving delivery updates, or refund processing estimates as if you have real system access."
            ),
            chat_ctx=chat_ctx
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=(
                "Kung nag Tagalog/Filipino ang user, sabihin mo ito: Magandang araw! Ito ang ShopBills customer support para sa mga basic na concern. Ano pong maitutulong namin sa inyo ngayon? "
                "If the user spoke English, say this: Good day! This is ShopBills customer support for basic concerns. How can we help you today?."
            )
        )

    @function_tool()
    async def escalate(self, reason: str):
        await self.session.generate_reply(
            instructions=(
                "Kung nag Tagalog/Filipino ang user, sabihin mo ito: I-e-escalate ko po ito ngayon. Ipapasa ko kayo sa isang senior support agent na makakatulong sa inyong concern. "
                "If the user spoke English, say this: I'll need to escalate your concern. I am now transferring you to a senior support agent to assist you."
            )
        )

        return Tier3Agent(reason=reason)

