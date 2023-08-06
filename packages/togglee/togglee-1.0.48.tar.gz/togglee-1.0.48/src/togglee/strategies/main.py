from togglee.strategies.context import context_strategy
from togglee.strategies.release import release_strategy

strategy_maps = {
    'release': release_strategy,
    'context': context_strategy,
}