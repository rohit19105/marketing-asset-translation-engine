from langgraph.graph import StateGraph, START, END
from models.segment import Segment
from graph.translation_state import TranslationState
from services.review_policy import ReviewPolicy

class QualityReviewGraph:
    """
    Manages confidence-based human review routing using LangGraph.

    Evaluates the confidence score of a translated segment and determines
    whether the segment should be routed for human review.
    """
    def __init__(self):
        """
        Initializes and compiles the LangGraph workflow for
        confidence-based human review routing.
        """
        builder = StateGraph(TranslationState)

        builder.add_node("review_decision", self.review_decision_node)

        builder.add_edge(START, "review_decision")

        builder.add_conditional_edges(
            "review_decision",
            self.route_review,
            {
                "approved": END,
                "human_review": END
            }
        )

        self.graph = builder.compile()


    def review_decision_node(self, state: TranslationState) -> dict:
        """
        Determines whether a translated segment requires human review.

        :param state: Current LangGraph translation state.

        :return: Updated state containing the human-review decision.
        """
        confidence = state["confidence_score"]

        requires_review = ReviewPolicy.requires_review(confidence)

        return {
            "requires_human_review": requires_review
        }


    def route_review(self, state: TranslationState) -> str:
        """
        Routes the workflow based on the human-review decision.

        :param state: Current LangGraph translation state.

        :return: Name of the next graph node.
        """
        if state["requires_human_review"]:
            return "human_review"

        return "approved"


    def run(self, segment: Segment, confidence_score: float) -> TranslationState:
        """
        Executes the quality review graph for a translated segment.

        :param segment: Translated segment to evaluate.
        :param confidence_score: Calculated confidence score for the segment.

        :return: Final TranslationState containing the human-review decision.
        """
        initial_state = {
            "segment": segment,
            "confidence_score": confidence_score,
            "requires_human_review": False
        }

        return self.graph.invoke(initial_state)