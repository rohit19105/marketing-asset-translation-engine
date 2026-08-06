class ReviewPolicy:
    """
    Determines whether a translation should be routed
    for human review based on its confidence score.
    """

    REVIEW_THRESHOLD = 0.90
    #REVIEW_THRESHOLD = 1.01  #For Testing

    @staticmethod
    def requires_review(confidence: float) -> bool:
        """
        Determines whether human review is required.

        :param confidence: Confidence score of the translated segment.

        :return: True if the confidence score is below the review threshold;
                 otherwise False.
        """
        return confidence < ReviewPolicy.REVIEW_THRESHOLD