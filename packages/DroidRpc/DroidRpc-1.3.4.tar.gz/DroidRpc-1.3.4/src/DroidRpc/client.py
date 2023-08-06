# Python client for connecting to LORA Technologies' bot services

__author__ = "LORA Technologies"
__email__ = "asklora@loratechai.com"

from ast import Try
from io import BytesIO
from typing import Optional, List, Generator, Union
import grpc
from .grpc_interface import bot_pb2_grpc, bot_pb2
from datetime import datetime
from .converter import (
    datetime_to_timestamp,
    array_to_bytes,
    bytes_to_array,
    protobuf_to_dict,
)
from .dataclasses import create_inputs, hedge_inputs, stop_inputs
import math
import numpy as np
import json
from timeit import default_timer as timer
from datetime import timedelta

# TODO use pydantic dataclass to validate field types.


class Client:
    def __init__(self, address: str = "guardian", port: str = "50065"):
        self.address = address
        self.port = port
        # TODO: Use a secure channel because this is external facing
        self.channel = grpc.insecure_channel(self.address + ":" + self.port)
        self.droid = bot_pb2_grpc.DroidStub(
            self.channel
        )  # This one contains the bistream

    def __string_to_datetime(self, date: str):
        date = datetime.strptime(date, "%Y-%m-%d")
        time = datetime.now().time()

        date_class = datetime_to_timestamp(datetime.combine(date, time))
        return date_class

    def create_bot(
        self,
        ticker: str,
        spot_date: str,
        investment_amount: float,
        bot_id: str,
        margin: int = 1,
        price: float = None,
        fractionals: bool = False,
        tp_multiplier: Optional[float] = None,
        sl_multiplier: Optional[float] = None,
    ):
        response = self.droid.CreateBot(
            bot_pb2.Create(
                ticker=ticker,
                spot_date=self.__string_to_datetime(spot_date),
                investment_amount=investment_amount,
                price=price,
                bot_id=bot_id,
                margin=margin,
                fraction=fractionals,
                tp_multiplier=tp_multiplier,
                sl_multiplier=sl_multiplier,
            )
        )
        return json.loads(response.message)

    def __create_bots_generator(self, input_matrix: np.array):
        """
        Generator function to be passed to the create_bots() gRPC bistream function.
        Splits a matrix of inputs into sub-batches and streams these sub-batches to Droid.

        Args:
            input_matrix (np.array(9,1)): List of inputs for each bot. The format is each row corresponds to the BatchCreate protobuf message.
        """

        # Split input matrix into smaller batches
        batch_size = 400
        splits = math.ceil(input_matrix.shape[1] / batch_size)
        input_matrix = np.array_split(input_matrix, splits, axis=1)

        for batch in input_matrix:
            try:
                message = bot_pb2.BatchCreate(
                    tickers=array_to_bytes(batch[0].astype("U7")),
                    spot_dates=array_to_bytes(batch[1].astype(np.datetime64)),
                    investment_amounts=array_to_bytes(batch[2].astype(float)),
                    prices=array_to_bytes(batch[3].astype(float)),
                    bot_ids=array_to_bytes(batch[4].astype(str)),
                    margins=array_to_bytes(batch[5].astype(float)),
                    fractions=array_to_bytes(batch[6].astype(bool)),
                    tp_multipliers=array_to_bytes(batch[7].astype(float)),
                    sl_multipliers=array_to_bytes(batch[8].astype(float)),
                )
            except TypeError as e:
                print(e)
            except Exception as e:
                print(e)
            # print(message.__sizeof__())

            yield message

    def __batch_response_generator(self, responses):
        """
        Generator function that wraps the gRPC bistream generator to convert bytes into numpy arrays

        Args:
            responses (generator obj): The gRPC bistream generator obj.
        """
        for response in responses:
            try:
                output = {
                    field: bytes_to_array(value)
                    for (field, value) in protobuf_to_dict(response).items()
                }
                output = np.array([row[1] for row in output.items()])
                output = np.rot90(output)
                print(output)
            except TypeError as e:
                print(e)
            except Exception as e:
                print(e)
            yield output

    def create_bots(
        self,
        create_inputs: Union[List[create_inputs], Generator],
        input_type: str = "list",
    ):
        """
        Returns a list of bots as dictionaries.

        Args:
            create_inputs (List[create_inputs]): Inputs for bot create.
        Kwargs:
            input_type (str): Type of accepted inputs. Defaults to 'list'.
                list : List of create_inputs dataclass objs
                generator : Generator obj that yields lists of inputs

        Returns:
            Generator: Generator of responses from Droid.
        """
        if input_type == "list":
            # Convert the inputs into numpy arrays
            start = timer()
            input_matrix = np.empty([1, 9])
            for i in create_inputs:
                arr = np.array(
                    [
                        [
                            i.ticker,
                            np.datetime64(i.spot_date),
                            i.investment_amount,
                            i.price,
                            i.bot_id,
                            i.margin,
                            i.fractionals,
                            i.tp_multiplier,
                            i.sl_multiplier,
                        ]
                    ]
                )
                input_matrix = np.concatenate(
                    (input_matrix, arr)
                )  # TODO: Fix crazy memory allocations
            input_matrix = np.delete(input_matrix, 0, 0)
            print(f"Total Numpy Conversion time: {timedelta(seconds=(timer()-start))}")

            # Rotate matrix
            input_matrix = np.rot90(input_matrix, k=-1)

            return self.__batch_response_generator(
                self.droid.CreateBots(self.__create_bots_generator(input_matrix))
            )

        elif input_type == "generator":
            # This is so that we can pipeline bot creation
            return self.droid.CreateBots(create_inputs)

        else:
            raise ValueError(f"{input_type} is not a valid type")

    def hedge(
        self,
        bot_id: str,
        ticker: str,
        current_price: float,
        entry_price: float,
        last_share_num: float,
        last_hedge_delta: float,
        investment_amount: float,
        bot_cash_balance: float,
        stop_loss_price: float,
        take_profit_price: float,
        expiry: str,
        strike: Optional[float] = None,
        strike_2: Optional[float] = None,
        margin: Optional[int] = 1,
        fractionals: Optional[bool] = False,
        option_price: Optional[float] = None,
        barrier: Optional[float] = None,
        current_low_price: Optional[float] = None,
        current_high_price: Optional[float] = None,
        ask_price: Optional[float] = None,
        bid_price: Optional[float] = None,
        trading_day: Optional[str] = datetime.strftime(
            datetime.now().date(), "%Y-%m-%d"
        ),
    ):
        response = self.droid.HedgeBot(
            bot_pb2.Hedge(
                ric=ticker,
                expiry=self.__string_to_datetime(expiry),
                investment_amount=investment_amount,
                current_price=current_price,
                bot_id=bot_id,
                margin=margin,
                entry_price=entry_price,
                last_share_num=last_share_num,
                last_hedge_delta=last_hedge_delta,
                bot_cash_balance=bot_cash_balance,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                option_price=option_price,
                strike=strike,
                strike_2=strike_2,
                barrier=barrier,
                current_low_price=current_low_price,
                current_high_price=current_high_price,
                ask_price=ask_price,
                bid_price=bid_price,
                fraction=fractionals,
                trading_day=self.__string_to_datetime(trading_day),
            )
        )
        return json.loads(response.message)

    def __hedge_bots_generator(self, input_matrix: np.array):
        """
        Generator function to be passed to the hedge_bots() gRPC bistream function.
        Splits a matrix of inputs into sub-batches and streams these sub-batches to Droid.

        Args:
            input_matrix (np.array(9,1)): List of inputs for each bnot. The format is each row corresponds to the BatchHedge protobuf message.
        """

        # Split input matrix into smaller batches
        batch_size = 400
        splits = math.ceil(input_matrix.shape[1] / batch_size)
        input_matrix = np.array_split(input_matrix, splits, axis=1)

        for batch in input_matrix:
            try:
                message = bot_pb2.BatchHedge(
                    bot_ids=array_to_bytes(batch[0].astype(str)),
                    tickers=array_to_bytes(batch[1].astype("U7")),
                    current_prices=array_to_bytes(batch[2].astype(float)),
                    entry_prices=array_to_bytes(batch[3].astype(float)),
                    last_share_nums=array_to_bytes(batch[4].astype(float)),
                    last_hedge_deltas=array_to_bytes(batch[5].astype(float)),
                    investment_amounts=array_to_bytes(batch[6].astype(float)),
                    bot_cash_balances=array_to_bytes(batch[7].astype(float)),
                    stop_loss_prices=array_to_bytes(batch[8].astype(float)),
                    take_profit_prices=array_to_bytes(batch[9].astype(float)),
                    expirys=array_to_bytes(batch[10].astype(np.datetime64)),
                    strikes=array_to_bytes(batch[11].astype(float)),
                    strike_2s=array_to_bytes(batch[12].astype(float)),
                    margins=array_to_bytes(batch[13].astype(int)),
                    fractions=array_to_bytes(batch[14].astype(bool)),
                    option_prices=array_to_bytes(batch[15].astype(float)),
                    barriers=array_to_bytes(batch[16].astype(float)),
                    current_low_prices=array_to_bytes(batch[17].astype(float)),
                    current_high_prices=array_to_bytes(batch[18].astype(float)),
                    ask_prices=array_to_bytes(batch[19].astype(float)),
                    bid_prices=array_to_bytes(batch[20].astype(float)),
                    trading_days=array_to_bytes(batch[21].astype(np.datetime64)),
                )
            except TypeError as e:
                print(e)
            except Exception as e:
                print(e)
            # print(message.__sizeof__())

            yield message

    def hedge_bots(
        self,
        hedge_inputs: Union[List[hedge_inputs], Generator],
        input_type: str = "list",
    ):
        """
        Returns a list of bots as dictionaries.

        Args:
            hedge_inputs (List[hedge_inputs]): Inputs for bot creation.
        Kwargs:
            input_type (str): Type of accepted inputs. Defaults to 'list'.
                list : List of hedge_inputs dataclass objs
                generator : Generator obj that yields lists of inputs

        Returns:
            Generator: Generator of responses from Droid.
        """
        if input_type == "list":
            print("hedging")
            # Convert inputs into np.ndarrays
            input_matrix = np.empty([1, 22])
            for i in hedge_inputs:
                arr = np.array(
                    [
                        [
                            i.bot_id,
                            i.ric,
                            i.current_price,
                            i.entry_price,
                            i.last_share_num,
                            i.last_hedge_delta,
                            i.investment_amount,
                            i.bot_cash_balance,
                            i.stop_loss_price,
                            i.take_profit_price,
                            np.datetime64(i.expiry),
                            i.strike,
                            i.strike_2,
                            i.margin,
                            i.fractionals,
                            i.option_price,
                            i.barrier,
                            i.current_low_price,
                            i.current_high_price,
                            i.ask_price,
                            i.bid_price,
                            np.datetime64(i.trading_day),
                        ]
                    ]
                )
                input_matrix = np.concatenate(
                    (input_matrix, arr)
                )  # TODO: Fix crazy memory allocations
            input_matrix = np.delete(input_matrix, 0, 0)

            # Rotate matrix
            input_matrix = np.rot90(input_matrix, k=-1)

            generator = self.__hedge_bots_generator(input_matrix)
            hedgeBots = self.droid.HedgeBots(generator)
            outputGenerator = self.__batch_response_generator(hedgeBots)
            return outputGenerator

        elif input_type == "generator":
            return self.droid.HedgeBots(hedge_inputs)
        else:
            raise ValueError(f"{input_type} is not a valid type")

    def stop(
        self,
        bot_id: str,
        ticker: str,
        current_price: float,
        entry_price: float,
        last_share_num: float,
        last_hedge_delta: float,
        investment_amount: float,
        bot_cash_balance: float,
        stop_loss_price: float,
        take_profit_price: float,
        expiry: str,
        strike: Optional[float] = None,
        strike_2: Optional[float] = None,
        margin: Optional[int] = 1,
        fractionals: Optional[bool] = False,
        option_price: Optional[float] = None,
        barrier: Optional[float] = None,
        current_low_price: Optional[float] = None,
        current_high_price: Optional[float] = None,
        ask_price: Optional[float] = None,
        bid_price: Optional[float] = None,
        trading_day: Optional[str] = datetime.strftime(
            datetime.now().date(), "%Y-%m-%d"
        ),
    ):
        response = self.droid.StopBot(
            bot_pb2.Stop(
                ric=ticker,
                expiry=self.__string_to_datetime(expiry),
                investment_amount=investment_amount,
                current_price=current_price,
                bot_id=bot_id,
                margin=margin,
                entry_price=entry_price,
                last_share_num=last_share_num,
                last_hedge_delta=last_hedge_delta,
                bot_cash_balance=bot_cash_balance,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                option_price=option_price,
                strike=strike,
                strike_2=strike_2,
                barrier=barrier,
                current_low_price=current_low_price,
                current_high_price=current_high_price,
                ask_price=ask_price,
                bid_price=bid_price,
                fraction=fractionals,
                trading_day=self.__string_to_datetime(trading_day),
            )
        )
        return json.loads(response.message)

    def __stop_bots_generator(
        self,
        input_matrix: np.ndarray,
    ):
        batch_size = 400
        splits = math.ceil(input_matrix.shape[1] / batch_size)
        input_matrix = np.array_split(input_matrix, splits, axis=1)

        for batch in input_matrix:
            try:
                message = bot_pb2.BatchStop(
                    bot_ids=array_to_bytes(batch[0].astype(str)),
                    tickers=array_to_bytes(batch[1].astype("U7")),
                    current_prices=array_to_bytes(batch[2].astype(float)),
                    entry_prices=array_to_bytes(batch[3].astype(float)),
                    last_share_nums=array_to_bytes(batch[4].astype(float)),
                    last_hedge_deltas=array_to_bytes(batch[5].astype(float)),
                    investment_amounts=array_to_bytes(batch[6].astype(float)),
                    bot_cash_balances=array_to_bytes(batch[7].astype(float)),
                    stop_loss_prices=array_to_bytes(batch[8].astype(float)),
                    take_profit_prices=array_to_bytes(batch[9].astype(float)),
                    expirys=array_to_bytes(batch[10].astype(np.datetime64)),
                    strikes=array_to_bytes(batch[11].astype(float)),
                    strike_2s=array_to_bytes(batch[12].astype(float)),
                    margins=array_to_bytes(batch[13].astype(int)),
                    fractions=array_to_bytes(batch[14].astype(bool)),
                    option_prices=array_to_bytes(batch[15].astype(float)),
                    barriers=array_to_bytes(batch[16].astype(float)),
                    current_low_prices=array_to_bytes(batch[17].astype(float)),
                    current_high_prices=array_to_bytes(batch[18].astype(float)),
                    ask_prices=array_to_bytes(batch[19].astype(float)),
                    bid_prices=array_to_bytes(batch[20].astype(float)),
                    trading_days=array_to_bytes(batch[21].astype(np.datetime64)),
                )
            except TypeError as e:
                print(e)
            except Exception as e:
                print(e)

            yield message

    def stop_bots(
        self, stop_inputs: Union[List[stop_inputs], Generator], input_type: str = "list"
    ):

        if input_type == "list":
            # Convert the inputs into numpy arrays
            input_matrix = np.empty([1, 22])
            for i in stop_inputs:
                arr = np.array(
                    [
                        [
                            i.bot_id,
                            i.ric,
                            i.current_price,
                            i.entry_price,
                            i.last_share_num,
                            i.last_hedge_delta,
                            i.investment_amount,
                            i.bot_cash_balance,
                            i.stop_loss_price,
                            i.take_profit_price,
                            i.expiry,
                            i.strike,
                            i.strike_2,
                            i.margin,
                            i.fractionals,
                            i.option_price,
                            i.barrier,
                            i.current_low_price,
                            i.current_high_price,
                            i.ask_price,
                            i.bid_price,
                            i.trading_day,
                        ]
                    ]
                )
                input_matrix = np.concatenate(
                    (input_matrix, arr)
                )  # TODO: Fix crazy memory allocations
            input_matrix = np.delete(input_matrix, 0, 0)

            input_matrix = np.rot90(input_matrix, k=-1)

            return self.__batch_response_generator(
                self.droid.StopBots(self.__stop_bots_generator(input_matrix))
            )

        elif input_type == "generator":
            return self.droid.CreateBots(create_inputs)

        else:
            raise ValueError(f"{input_type} is not a valid type")
