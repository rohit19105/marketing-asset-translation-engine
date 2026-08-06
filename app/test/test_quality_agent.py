from agents.quality_agent import QualityAgent
from models.segment import Segment
from services.llm_factory import LLMFactory


llm = LLMFactory.create()

quality_agent = QualityAgent(llm)

segment = Segment(
    segment_id="test_001",
    source_text="Build the next generation of AI-powered composable solutions"
)

bad_translation = "Me gusta comer pizza."

result = quality_agent.evaluate(
    segment=segment,
    translated_text=bad_translation
)

print("\nQUALITY RESULT:")
print(result)