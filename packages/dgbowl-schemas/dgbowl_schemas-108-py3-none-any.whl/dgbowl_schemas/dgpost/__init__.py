from pydantic import ValidationError
import logging
from .recipe_1_1 import Recipe as Recipe_1_1
from .recipe_1_0 import Recipe as Recipe_1_0

logger = logging.getLogger(__name__)

latest_version = "1.1"
Recipe = Recipe_1_1


def to_recipe(**kwargs):
    models = {
        "1.1": Recipe_1_1,
        "1.0": Recipe_1_0,
    }
    firste = None
    for ver, Model in models.items():
        try:
            payload = Model(**kwargs)
            return payload
        except ValidationError as e:
            logger.warning("Could not parse 'kwargs' using Recipe v%s.", ver)
            logger.warning(e)
            if firste is None:
                firste = e
    raise ValueError(firste)
