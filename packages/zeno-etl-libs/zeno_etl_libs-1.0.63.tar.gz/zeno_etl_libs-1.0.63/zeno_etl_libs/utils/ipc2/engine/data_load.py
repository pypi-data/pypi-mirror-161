class LoadData:

    def load_file(self, db, query):
        df = db.get_df(query)
        df.columns = [c.replace('-', '_') for c in df.columns]
        return df

    def load_all_input(
            self,
            type_list=None,
            store_id_list=None,
            last_date=None,
            reset_date=None,
            schema=None,
            db=None
    ):
        drug_list = self.load_file(
            query="""
                select id as drug_id from "{schema}".drugs where type in {0}
                 """.format(type_list, schema=schema),
            db=db
        )

        sales_history = self.load_file(
            query="""
                select date("created-at") as "sales-date","store-id", "drug-id" , 
                        sum("net-quantity") as "net-sales-quantity"
                from "{schema}".sales s
                where "store-id" in {store_id_list}
                and date("created-at") >= '{last_date}'
                and date("created-at") < '{reset_date}'
                group by "store-id",  "drug-id", "sales-date"
                """.format(
                store_id_list=store_id_list, last_date=last_date,
                reset_date=reset_date, schema=schema),
            db=db
        )

        cfr_pr = self.load_file(
            query=f"""
                select "store-id", "drug-id","shortbook-date", 
                sum("loss-quantity") as "loss-quantity"
                from "{schema}"."cfr-patient-request"
                where "shortbook-date" >= '{last_date}'
                and "shortbook-date" < '{reset_date}'
                and "drug-id" <> -1
                and ("drug-category" = 'chronic' or "repeatability-index" >= 40)
                and "loss-quantity" > 0
                and "drug-type" in {type_list}
                and "store-id" in {store_id_list}
                group by "store-id","drug-id", "shortbook-date"
                """,
            db=db
        )

        calendar = self.load_file(
            query="""
                select date, year, month, "week-of-year", "day-of-week" 
                from "{schema}".calendar
                where date < '{reset_date}'
                """.format(schema=schema, reset_date=reset_date),
            db=db
        )

        first_bill_date = self.load_file(
            query="""
                select "store-id" , min(date("created-at")) as bill_date from "{schema}".sales
                where "store-id" in {store_id_list}
                group by "store-id" 
                """.format(schema=schema, store_id_list=store_id_list),
            db=db
        )

        return (
            drug_list,
            sales_history,
            cfr_pr,
            calendar,
            first_bill_date
        )
