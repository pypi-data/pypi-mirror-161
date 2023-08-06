from typing import List, Optional

from core.oracle.Prediction import Prediction
from exchange.rate.ExchangeRateHolder import ExchangeRateHolder

from oracle.Oracle import Oracle


class PredictionResolver:

    def __init__(self, oracles):
        self.oracles: List[Oracle] = oracles

    def resolve(self, instrument, exchange_rates, exchanged_from, instant) -> Optional[Prediction]:
        self.set_all_oracle_with_exchange_rates(exchange_rates)
        predictions = self.collect_predictions_from_oracles(instrument, exchanged_from, instant)
        best_prediction = self.determine_best_prediction(predictions)
        if best_prediction is not None:
            self.reset_oracles()
            return best_prediction

    def set_all_oracle_with_exchange_rates(self, exchange_rates: ExchangeRateHolder):
        for oracle in self.oracles:
            oracle.set_exchange_rates(exchange_rates)

    def collect_predictions_from_oracles(self, instrument, exchanged_from, instant) -> List[Prediction]:
        predictions = []
        for oracle in self.oracles:
            prediction = oracle.predict(instrument, exchanged_from, instant)
            predictions.append(prediction)
        valid_predictions = [p for p in predictions if p is not None]
        return valid_predictions

    def determine_best_prediction(self, predictions: List[Prediction]):
        if not predictions:
            return None
        sorted_predictions = sorted(predictions, key=lambda prediction: prediction.percent, reverse=True)
        return self.designate_appropriate_prediction(sorted_predictions)

    def designate_appropriate_prediction(self, predictions: List[Prediction]):
        # todo: if predictions are below (need to coerce to trade)
        # todo: threshold is one mechanism
        # todo: hook provider to trader to influence "coercion"
        forced_prediction = self.obtain_best_forced_prediction(predictions)
        return forced_prediction if forced_prediction is not None else self.obtain_best_prediction(predictions)

    @staticmethod
    def obtain_best_forced_prediction(predictions):
        forced_predictions = [p for p in predictions if p.forced is True]
        if len(forced_predictions) > 0:
            return forced_predictions[0]

    @staticmethod
    def obtain_best_prediction(predictions):
        if len(predictions) > 0:
            return predictions[0]

    def reset_oracles(self):
        for oracle in self.oracles:
            oracle.reset()

