from time import strptime
from silal_payments import db
from sqlalchemy import text
from sqlalchemy.engine import Result, Row
from silal_payments.models.transactions.transaction import Transaction, TransactionType

import datetime


class SellerCompanyTransaction(Transaction):
    sub_table_name = "seller_company_transaction"

    def __init__(
        self,
        transaction_id: int,
        transaction_amount: float,
        transaction_date: datetime,
        seller_id: int,
    ):
        super().__init__(
            transaction_id,
            TransactionType.seller_company_transaction,
            transaction_amount,
            transaction_date,
        )
        self.seller_id = seller_id

    def insert_into_db(self):
        super().insert_into_db()
        stmt = text(
            f"""INSERT INTO public.{self.sub_table_name} (seller_id, transaction_id) VALUES (:seller_id, :transaction_id);"""
        ).bindparams(
            seller_id=self.seller_id,
            transaction_id=self.transaction_id,
        )

        db.session.execute(stmt)
        db.session.commit()


def load_seller_company_transaction_from_db(
    transaction_id: int,
) -> SellerCompanyTransaction:
    """Load a seller_company_transaction from the database"""
    stmt = text(
        f"""
        SELECT
            public.{SellerCompanyTransaction.sub_table_name}.transaction_id,
            public.{Transaction.table_name}.transaction_amount,
            public.{Transaction.table_name}.transaction_date,
            public.{SellerCompanyTransaction.sub_table_name}.seller_id
        FROM public.{SellerCompanyTransaction.sub_table_name}
        INNER JOIN public.{Transaction.table_name}
        ON public.{SellerCompanyTransaction.sub_table_name}.transaction_id = public.{Transaction.table_name}.transaction_id
        WHERE public.{SellerCompanyTransaction.sub_table_name}.transaction_id = :transaction_id;
        """
    ).bindparams(transaction_id=transaction_id)
    result: Result = db.session.execute(stmt)
    transaction: Row = result.first()

    if transaction is None:
        return None

    return SellerCompanyTransaction(
        transaction_id=transaction[0],
        transaction_amount=transaction[1],
        transaction_date=transaction[2],
        seller_id=transaction[3],
    )
