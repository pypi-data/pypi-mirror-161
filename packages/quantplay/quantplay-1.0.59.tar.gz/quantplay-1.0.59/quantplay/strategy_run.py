from quantplay.strategies.options.intraday.musk import Musk
from quantplay.executor.strategy_executor import UserStrategiesExecutor
strategies = [()]

UserStrategiesExecutor("Zerodha", strategies).start_execution()