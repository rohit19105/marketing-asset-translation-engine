from models.quality_result import QualityResult


class ConfidenceCalculator:
    """
    Calculates the overall confidence score from individual
    quality evaluation scores.
    """

    @staticmethod
    def calculate(result: QualityResult) -> float:
        """
        Computes a weighted confidence score.

        Weights:
        - Accuracy: 40%
        - Brand tone: 20%
        - Glossary adherence: 30%
        - Formatting: 10%

        :param result: Quality evaluation scores for a translated segment.

        :return: Weighted confidence score between 0.0 and 1.0.
        """

        confidence = (
            result.accuracy_score * 0.4
            + result.brand_tone_score * 0.2
            + result.glossary_score * 0.3
            + result.formatting_score * 0.1
        )

        return round(confidence, 3)