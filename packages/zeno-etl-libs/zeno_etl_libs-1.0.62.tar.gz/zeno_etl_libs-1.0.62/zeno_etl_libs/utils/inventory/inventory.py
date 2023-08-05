import datetime

import numpy as np
# from memory_profiler import profile

import pandas as pd


def remove_duplicates(df: pd.DataFrame, f):
    """
    TODO: implement this function

    #remove duplicates from dataframe of the form id, f, ptr
    #f corresponds to quantity which is added up for duplicate ids
    #ptr remains same for all

    function remove_duplicates(df, f)
        if nrow(df) == 0
            return df
        end

        gd = groupby(df, :id)
        combined = DataFrame()
        for g in gd
            local s = 0
            for r in eachrow(g)
                s += r[Symbol(f)]
            end
            combined = vcat(combined, DataFrame(
                               id = [g[!, :id][1]],
                               barcode = [g[!, :barcode][1]],
                               qty = [s],
                               ptr = [g[!, :ptr][1]]))
        end

        combined = select(combined, :id, :barcode, :qty => Symbol(f), :ptr)
    end
    """
    print(f"Removed duplicates on column: {f}")
    df1 = df.groupby('id', as_index=False)[f].sum()
    df2 = df.drop_duplicates(subset='id').drop(columns=f)
    df = pd.merge(left=df1, right=df2, on='id', how='left')
    return df


def getids(df: pd.DataFrame):
    """
    utility function to generate string to be used in "in" query
    """
    return (",").join(str(i) for i in df['id'].unique())


def combin_xin(recon_l: pd.DataFrame, xin_l: pd.DataFrame):
    """
    this will take care of stores own inventory coming back
    """

    """
    function combine_xin(recon_l, xin_l)
        ##
        recon_l = leftjoin(recon_l, select(xin_l, :id, :xin), on = :id, makeunique = true)
        ## for xin we cannot do a just left join because the incoming 
        #inventorhy may or may not be in the opening list
        #
        #First find all new inventories
        temp = antijoin(xin_l, recon_l, on = :id)
        #add missing columns so we can combine with recon_l
        insertcols!(temp, 2, :o => missing)
        insertcols!(temp, 3, :cr => missing)
        temp = select(temp, :id, :barcode, :o, :ptr, :cr, :xin)
        recon_l = vcat(recon_l, temp)
        return recon_l
    end
    """
    return pd.concat([recon_l, xin_l], axis=0).drop_duplicates(subset='id')


class Data:
    """
    class to get the inventory related data

    Example:
        'o', 'cr', 'xin', 'xout', 'ret', 'sold', 'del', 'ar', 'rr', 'c'
    """

    def __init__(self, db, csv_store_ids, start_date, end_date):
        """
        :param db: database connection
        :param csv_store_ids: multiple store ids in csv
        :param start_date: start date in IST
        :param end_date: end date in IST
        """

        self.db = db
        self.csv_store_ids = csv_store_ids
        # current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        # self.end_ts = f"{end_date} 03:00:00" if end_date else f"{current_date} 03:00:00" # in IST
        self.start_ts = f"{start_date}  02:00:00"  # in IST
        self.end_ts = f"{end_date} 03:00:00"  # in IST

        """ since snapshots names are in UTC so tables alias is one day back"""
        start_date_utc = datetime.datetime.strptime(start_date, '%Y-%m-%d') + datetime.timedelta(days=-1)
        start_date_utc = start_date_utc.strftime("%Y-%m-%d")

        end_date_utc = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=-1)
        end_date_utc = end_date_utc.strftime("%Y-%m-%d")

        self.s_alias = f"-mis-{start_date_utc}"
        if start_date == "2022-06-01":
            # Only for  2022-06-01 manual snapshot, since snapshot name and date are same
            self.s_alias = f"-mis-{start_date}"
            # self.e_alias = f"-mis-{end_date}" if end_date else ""
        self.e_alias = f"-mis-{end_date_utc}"

        self.s_schema = "public"
        self.e_schema = "public"
        # self.e_schema = "public" if end_date else "prod2-generico"

        """ Data frames """
        self.recon_l = pd.DataFrame()  # Final reconciled data frame
        self.p_l = pd.DataFrame()  # purchased / received
        self.o_l = pd.DataFrame()  # opening / initial
        self.cr_l = pd.DataFrame()  #
        self.xin_l = pd.DataFrame()  #
        self.xout_l = pd.DataFrame()  #
        self.sold_l = pd.DataFrame()  #
        self.ret_l = pd.DataFrame()  #
        self.ar_l = pd.DataFrame()  #
        self.rr_l = pd.DataFrame()  #
        self.del_l = pd.DataFrame()  #
        self.c_l = pd.DataFrame()  #

    def take_union(self):
        """
        select one value of barcode from left or right data frame
        """
        for col in ['barcode', 'ptr']:
            self.recon_l[col] = np.where(self.recon_l[f'{col}_x'].isna(), self.recon_l[f'{col}_y'],
                                         self.recon_l[f'{col}_x'])
            self.recon_l.drop(columns=[f'{col}_x', f'{col}_y'], axis=1, inplace=True)

    def opening(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        DataFrame(DBInterface.execute(conn, "use `mis-$start_date`"))
        q = "select id, ifnull(`barcode-reference`, 0) barcode, quantity o, ptr from `inventory-1` where
            `store-id` = $store_id and `barcode-reference` is null order by id"
        o_l_1 = DataFrame(DBInterface.execute(conn, q))
        q = "select id, ifnull(`barcode-reference`, 0) barcode, quantity o, ptr from `inventory-1` where
            `store-id` = $store_id and `barcode-reference` is not null order by id"
        o_l_2 = DataFrame(DBInterface.execute(conn, q))
        o_l = vcat(o_l_1, o_l_2)
        """

        q = f"""
        select
            id,
            nvl("barcode-reference", 0) barcode,
            quantity o,
            ptr
        from
            "{self.s_schema}"."inventory-1{self.s_alias}"
        where
            "store-id" in ({self.csv_store_ids})
            and "barcode-reference" is null
            and quantity != 0
        order by
            id
        """
        o_l_1 = self.db.get_df(query=q)

        q = f"""
            select
                id,
                nvl("barcode-reference", 0) barcode,
                quantity o,
                ptr
            from
                "{self.s_schema}"."inventory-1{self.s_alias}"
            where
                "store-id" in ({self.csv_store_ids})
                and "barcode-reference" is not null
                and quantity != 0
            order by
                id
            """
        o_l_2 = self.db.get_df(query=q)

        self.o_l = pd.concat([o_l_1, o_l_2], ignore_index=True)
        return self.o_l

    def purchased(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        q = "
            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`actual-quantity` p, c.ptr
            from `invoice-items-1` a
            join `invoices-1` b on a.`franchisee-invoice-id` = b.id
            join `inventory-1` c on (c.`invoice-item-id` = a.id and c.`store-id` = $store_id)
            where b.`store-id` = $store_id and b.`received-at` >= '$start_ts' and
            b.`received-at` <= '$end_ts'
            "
        p_l = DataFrame(DBInterface.execute(conn, q))
        """

        q = f"""
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."actual-quantity" p,
            c.ptr
        from
            "{self.e_schema}"."invoice-items-1{self.e_alias}" a
        join "{self.e_schema}"."invoices-1{self.e_alias}" b on
            a."franchisee-invoice-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (c."invoice-item-id" = a.id
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and b."received-at" >= '{self.start_ts}'
            and b."received-at" <= '{self.end_ts}'
            and a."actual-quantity" !=0
        """
        self.p_l = self.db.get_df(query=q)
        return self.p_l

    def customer_returns(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")
        q = "
            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`returned-quantity` cr, c.ptr
                    from `customer-return-items-1` a
                    join `customer-returns-1` b on a.`return-id` = b.id
                join `inventory-1` c on (a.`inventory-id` = c.id and c.`store-id` = $store_id)
                    where b.`store-id` = $store_id and
                    b.`returned-at` >= '$start_ts' and b.`returned-at` <= '$end_ts'

            union all

            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`returned-quantity` cr, c.ptr
                    from `customer-return-items-1` a
                    join `customer-returns-1` b on a.`return-id` = b.id
                join `inventory-1` c on (a.`inventory-id` = c.`barcode-reference` and c.`store-id` = $store_id)
                    where b.`store-id` = $store_id and
                    b.`returned-at` >= '$start_ts' and b.`returned-at` <= '$end_ts'
        "
        cr_l = DataFrame(DBInterface.execute(conn, q))
        cr_l = remove_duplicates(cr_l, "cr")
        """
        q = f"""
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."returned-quantity" cr,
            c.ptr
        from
            "{self.e_schema}"."customer-return-items-1{self.e_alias}" a
        join "{self.e_schema}"."customer-returns-1{self.e_alias}" b on
            a."return-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c.id
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and b."returned-at" >= '{self.start_ts}'
            and b."returned-at" <= '{self.end_ts}'
            and a."returned-quantity" !=0
        union all
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."returned-quantity" cr,
            c.ptr
        from
            "{self.e_schema}"."customer-return-items-1{self.e_alias}" a
        join "{self.e_schema}"."customer-returns-1{self.e_alias}" b on
            a."return-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c."barcode-reference"
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and b."returned-at" >= '{self.start_ts}'
            and b."returned-at" <= '{self.end_ts}'
            and a."returned-quantity" !=0
        """

        self.cr_l = self.db.get_df(query=q)
        self.cr_l = remove_duplicates(df=self.cr_l, f="cr")
        return self.cr_l

    def xin(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        q = "
            select c.id, ifnull(`barcode-reference`, 0) barcode, a.quantity xin, c.ptr
            from `stock-transfer-items-1` a
            join `stock-transfers-1` b on a.`transfer-id` = b.id
            join `inventory-1` c on (a.`inventory-id` = c.id and c.`store-id` = $store_id)
            where b.`destination-store` = '$store_id'
            and b.`received-at` >= '$start_ts' and b.`received-at` <= '$end_ts'

            union all

            select c.id, ifnull(`barcode-reference`, 0) barcode, a.quantity xin, c.ptr
            from `stock-transfer-items-1` a
            join `stock-transfers-1` b on a.`transfer-id` = b.id
            join `inventory-1` c on (a.`inventory-id` = c.`barcode-reference` and c.`store-id` = $store_id)
            where b.`destination-store` = '$store_id'
            and b.`received-at` >= '$start_ts' and b.`received-at` <= '$end_ts'
        "
        xin_l = DataFrame(DBInterface.execute(conn, q))
        xin_l = remove_duplicates(xin_l, "xin")
        """
        q = f"""
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a.quantity xin,
            c.ptr
        from
            "{self.e_schema}"."stock-transfer-items-1{self.e_alias}" a
        join "{self.e_schema}"."stock-transfers-1{self.e_alias}" b on
            a."transfer-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c.id
                and c."store-id" = b."destination-store")
        where
            b."destination-store" in ({self.csv_store_ids})
            and b."received-at" >= '{self.start_ts}'
            and b."received-at" <= '{self.end_ts}'
            and a.quantity !=0
        union all
        
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a.quantity xin,
            c.ptr
        from
            "{self.e_schema}"."stock-transfer-items-1{self.e_alias}" a
        join "{self.e_schema}"."stock-transfers-1{self.e_alias}" b on
            a."transfer-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c."barcode-reference"
                and c."store-id" = b."destination-store")
        where
            b."destination-store" in ({self.csv_store_ids})
            and b."received-at" >= '{self.start_ts}'
            and b."received-at" <= '{self.end_ts}'
            and a.quantity !=0
        """
        self.xin_l = self.db.get_df(query=q)
        self.xin_l = remove_duplicates(df=self.xin_l, f="xin")
        return self.xin_l

    def xout(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        q = "
            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`quantity` xout, c.ptr
            from `stock-transfer-items-1` a
            join `stock-transfers-1` b on a.`transfer-id` = b.id
            join `inventory-1` c on (a.`inventory-id` = c.id and c.`store-id` = '$store_id')
            where b.`source-store` = '$store_id' and
            a.`transferred-at` >= '$start_ts' and a.`transferred-at` <= '$end_ts'

            union all

            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`quantity` xout, c.ptr
            from `stock-transfer-items-1` a
            join `stock-transfers-1` b on a.`transfer-id` = b.id
            join `inventory-1` c on (a.`inventory-id` = c.`barcode-reference` and c.`store-id` = $store_id)
            where b.`source-store` = '$store_id' and
            a.`transferred-at` >= '$start_ts' and a.`transferred-at` <= '$end_ts'

        "
        xout_l = DataFrame(DBInterface.execute(conn, q))
        xout_l = remove_duplicates(xout_l, "xout")
        """

        q = f"""
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."quantity" xout,
            c.ptr
        from
            "{self.e_schema}"."stock-transfer-items-1{self.e_alias}" a
        join "{self.e_schema}"."stock-transfers-1{self.e_alias}" b on
            a."transfer-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c.id
                and c."store-id" = b."source-store")
        where
            b."source-store" in ({self.csv_store_ids})
            and a."transferred-at" >= '{self.start_ts}'
            and a."transferred-at" <= '{self.end_ts}'
            and a.quantity !=0
        
        union all
        
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."quantity" xout,
            c.ptr
        from
            "{self.e_schema}"."stock-transfer-items-1{self.e_alias}" a
        join "{self.e_schema}"."stock-transfers-1{self.e_alias}" b on
            a."transfer-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c."barcode-reference"
                and c."store-id" = b."source-store")
        where
            b."source-store" in ({self.csv_store_ids})
            and a."transferred-at" >= '{self.start_ts}'
            and a."transferred-at" <= '{self.end_ts}'
            and a.quantity !=0    
        """
        self.xout_l = self.db.get_df(query=q)
        self.xout_l = remove_duplicates(self.xout_l, "xout")
        return self.xout_l

    def sold(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        q = "
            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`quantity` sold, c.ptr
            from `bill-items-1` a
            join `bills-1` b on a.`bill-id` = b.id
            join `inventory-1` c on (a.`inventory-id` = c.id and c.`store-id` = $store_id)
            where b.`store-id` = $store_id and b.`created-at` >= '$start_ts' and b.`created-at` <= '$end_ts'

            union all

            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`quantity` sold, c.ptr
            from `bill-items-1` a
            join `bills-1` b on a.`bill-id` = b.id
            join `inventory-1` c on (a.`inventory-id` = c.`barcode-reference` and c.`store-id` = $store_id)

            where b.`store-id` = $store_id and b.`created-at` >= '$start_ts' and b.`created-at` <= '$end_ts'
        "

        sold_l = DataFrame(DBInterface.execute(conn, q))
        sold_l = remove_duplicates(sold_l, "sold")
        """
        q = f"""
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."quantity" sold,
            c.ptr
        from
            "{self.e_schema}"."bill-items-1{self.e_alias}" a
        join "{self.e_schema}"."bills-1{self.e_alias}" b on
            a."bill-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c.id
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and b."created-at" >= '{self.start_ts}'
            and b."created-at" <= '{self.end_ts}'
            and a.quantity !=0
            
        union all 
        
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."quantity" sold,
            c.ptr
        from
            "{self.e_schema}"."bill-items-1{self.e_alias}" a
        join "{self.e_schema}"."bills-1{self.e_alias}" b on
            a."bill-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c."barcode-reference"
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and b."created-at" >= '{self.start_ts}'
            and b."created-at" <= '{self.end_ts}'
            and a.quantity !=0
        """
        self.sold_l = self.db.get_df(query=q)
        self.sold_l = remove_duplicates(self.sold_l, "sold")
        return self.sold_l

    def returned_to_dc(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        q = "
            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`returned-quantity` ret, c.ptr
                    from `return-items-1` a
                    join `returns-to-dc-1` b on a.`return-id` = b.id
                join `inventory-1` c on (a.`inventory-id` = c.id and c.`store-id` = $store_id)
                    where b.`store-id` = $store_id and b.`created-at` >= '$start_ts' and b.`created-at` <= '$end_ts'

            union all

            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`returned-quantity` ret, c.ptr
                    from `return-items-1` a
                    join `returns-to-dc-1` b on a.`return-id` = b.id
                join `inventory-1` c on (a.`inventory-id` = c.`barcode-reference` and c.`store-id` = $store_id)
                    where b.`store-id` = $store_id and b.`created-at` >= '$start_ts' and b.`created-at` <= '$end_ts'

        "
        ret_l = DataFrame(DBInterface.execute(conn, q))
        ret_l = remove_duplicates(ret_l, "ret")

        """
        q = f"""
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."returned-quantity" ret,
            c.ptr
        from
            "{self.e_schema}"."return-items-1{self.e_alias}" a
        join "{self.e_schema}"."returns-to-dc-1{self.e_alias}" b on
            a."return-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c.id
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and b."created-at" >= '{self.start_ts}'
            and b."created-at" <= '{self.end_ts}'
            and a."returned-quantity" !=0
        
        union all
        
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."returned-quantity" ret,
            c.ptr
        from
            "{self.e_schema}"."return-items-1{self.e_alias}" a
        join "{self.e_schema}"."returns-to-dc-1{self.e_alias}" b on
            a."return-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c."barcode-reference"
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and b."created-at" >= '{self.start_ts}'
            and b."created-at" <= '{self.end_ts}'
            and a."returned-quantity" !=0
        """
        self.ret_l = self.db.get_df(query=q)
        self.ret_l = remove_duplicates(self.ret_l, "ret")
        return self.ret_l

    def deleted(self):
        """
        db_start = "mis-$start_date"
        db_end = "mis-$end_date"

        DBInterface.execute(conn, "use `$db_start`")

        q = "
            select a.id, ifnull(`barcode-reference`, 0) barcode, a.quantity del, a.ptr
            from `inventory-1` a
            join `$db_end`.`deleted-invoices` c on a.`invoice-id` = c.id
            where a.`store-id` = $store_id and
            c.`deleted-at` >= '$start_ts' and c.`deleted-at` <= '$end_ts'

            union

            select a.id, ifnull(`barcode-reference`, 0) barcode, a.quantity del, a.ptr
            from `inventory-1` a
            join `$db_end`.`deleted-invoices-1` c on a.`franchisee-invoice-id` = c.id
            where a.`store-id` = $store_id and
            c.`deleted-at` >= '$start_ts' and c.`deleted-at` <= '$end_ts'
        "
        del_l = DataFrame(DBInterface.execute(conn, q))
        del_l = remove_duplicates(del_l, "del")


        """
        q = f"""
        select
            a.id,
            nvl("barcode-reference", 0) barcode,
            a.quantity del,
            a.ptr
        from
            "{self.s_schema}"."inventory-1{self.s_alias}" a
        join "{self.e_schema}"."deleted-invoices{self.e_alias}" c on
            a."invoice-id" = c.id
        where
            a."store-id" in ({self.csv_store_ids})
            and c."deleted-at" >= '{self.start_ts}'
            and c."deleted-at" <= '{self.end_ts}'
            and a.quantity !=0
            
        union
         
        select
            a.id,
            nvl("barcode-reference", 0) barcode,
            a.quantity del,
            a.ptr
        from
            "{self.s_schema}"."inventory-1{self.s_alias}" a
        join "{self.e_schema}"."deleted-invoices-1{self.e_alias}" c on
            a."franchisee-invoice-id" = c.id
        where
            a."store-id" in ({self.csv_store_ids})
            and c."deleted-at" >= '{self.start_ts}'
            and c."deleted-at" <= '{self.end_ts}'
            and a.quantity !=0
        """
        self.del_l = self.db.get_df(query=q)
        self.del_l = remove_duplicates(self.del_l, "del")
        return self.del_l

    def closing(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        DataFrame(DBInterface.execute(conn, "use `mis-$end_date`"))
        q = "select id, ifnull(`barcode-reference`, 0) barcode, quantity c, ptr from `inventory-1` where
            `store-id` = $store_id and `barcode-reference` is null order by id"
        c_l_1 = DataFrame(DBInterface.execute(conn, q))
        q = "select id, ifnull(`barcode-reference`, 0) barcode, quantity c, ptr from `inventory-1` where
            `store-id` = $store_id and `barcode-reference` is not null order by id"
        c_l_2 = DataFrame(DBInterface.execute(conn, q))
        c_l = vcat(c_l_1, c_l_2)
        """
        q = f"""
        select
            id,
            nvl("barcode-reference", 0) barcode,
            quantity c,
            ptr
        from
            "{self.e_schema}"."inventory-1{self.e_alias}"
        where
            "store-id" in ({self.csv_store_ids})
            and "barcode-reference" is null
            and quantity !=0
        order by
            id
        """
        c_l_1 = self.db.get_df(query=q)

        q = f"""
                select
                    id,
                    nvl("barcode-reference", 0) barcode,
                    quantity c,
                    ptr
                from
                    "{self.e_schema}"."inventory-1{self.e_alias}"
                where
                    "store-id" in ({self.csv_store_ids})
                    and "barcode-reference" is not null
                    and quantity !=0
                order by
                    id
                """
        c_l_2 = self.db.get_df(query=q)

        self.c_l = pd.concat([c_l_1, c_l_2], ignore_index=True)
        return self.c_l

    def audit_recon(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        q = "
            select b.id, ifnull(`barcode-reference`, 0) barcode, a.change ar, b.ptr
            from `inventory-changes-1` a
            join `inventory-1` b on (a.`inventory-id` = b.id and b.`store-id` = $store_id)
            where
            a.`store-id` = $store_id and a.`created-at` >= '$start_ts' and a.`created-at` <= '$end_ts'

            union all

            select b.id, ifnull(`barcode-reference`, 0) barcode, a.change ar, b.ptr
            from `inventory-changes-1` a
            join `inventory-1` b on (a.`inventory-id` = b.`barcode-reference` and b.`store-id` = $store_id)
            where
            a.`store-id` = $store_id and a.`created-at` >= '$start_ts' and a.`created-at` <= '$end_ts'

        "
        ar_l = DataFrame(DBInterface.execute(conn, q))
        ar_l = remove_duplicates(ar_l, "ar")
        """
        q = f"""
        select
            b.id,
            nvl("barcode-reference", 0) barcode,
            a.change ar,
            b.ptr
        from
            "{self.e_schema}"."inventory-changes-1{self.e_alias}" a
        join "{self.e_schema}"."inventory-1{self.e_alias}" b on
            (a."inventory-id" = b.id
                and b."store-id" = a."store-id")
        where
            a."store-id" in ({self.csv_store_ids})
            and a."created-at" >= '{self.start_ts}'
            and a."created-at" <= '{self.end_ts}'
            and a.change !=0
            
        union all
        
        select
            b.id,
            nvl("barcode-reference", 0) barcode,
            a.change ar,
            b.ptr
        from
            "{self.e_schema}"."inventory-changes-1{self.e_alias}" a
        join "{self.e_schema}"."inventory-1{self.e_alias}" b on
            (a."inventory-id" = b."barcode-reference"
                and b."store-id" = a."store-id")
        where
            a."store-id" in ({self.csv_store_ids})
            and a."created-at" >= '{self.start_ts}'
            and a."created-at" <= '{self.end_ts}'
            and a.change !=0
        """
        self.ar_l = self.db.get_df(query=q)
        self.ar_l = remove_duplicates(self.ar_l, "ar")
        return self.ar_l

    def reverted_returns(self):
        """
        db = "mis-$end_date"
        DBInterface.execute(conn, "use `$db`")

        q = "
            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`returned-quantity` rr, c.ptr
                    from `return-items-1` a
                    join `returns-to-dc-1` b on a.`return-id` = b.id
                join `inventory-1` c on (a.`inventory-id` = c.id and c.`store-id` = $store_id)
                    where b.`store-id` = $store_id and a.`reverted-at` >= '$start_ts' and a.`reverted-at` <= '$end_ts'

            union all

            select c.id, ifnull(`barcode-reference`, 0) barcode, a.`returned-quantity` rr, c.ptr
                    from `return-items-1` a
                    join `returns-to-dc-1` b on a.`return-id` = b.id
                join `inventory-1` c on (a.`inventory-id` = c.`barcode-reference` and c.`store-id` = $store_id)
                    where b.`store-id` = $store_id and a.`reverted-at` >= '$start_ts' and a.`reverted-at` <= '$end_ts'
        "

        rr_l = DataFrame(DBInterface.execute(conn, q))
        rr_l = remove_duplicates(rr_l, "rr")
        """
        q = f"""
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."returned-quantity" rr,
            c.ptr
        from
            "{self.e_schema}"."return-items-1{self.e_alias}" a
        join "{self.e_schema}"."returns-to-dc-1{self.e_alias}" b on
            a."return-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c.id
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and a."reverted-at" >= '{self.start_ts}'
            and a."reverted-at" <= '{self.end_ts}'
            and a."returned-quantity" !=0
            
        union all 
        
        select
            c.id,
            nvl("barcode-reference", 0) barcode,
            a."returned-quantity" rr,
            c.ptr
        from
            "{self.e_schema}"."return-items-1{self.e_alias}" a
        join "{self.e_schema}"."returns-to-dc-1{self.e_alias}" b on
            a."return-id" = b.id
        join "{self.e_schema}"."inventory-1{self.e_alias}" c on
            (a."inventory-id" = c."barcode-reference"
                and c."store-id" = b."store-id")
        where
            b."store-id" in ({self.csv_store_ids})
            and a."reverted-at" >= '{self.start_ts}'
            and a."reverted-at" <= '{self.end_ts}'
            and a."returned-quantity" !=0
        """
        self.rr_l = self.db.get_df(query=q)
        self.rr_l = remove_duplicates(self.rr_l, "rr")
        return self.rr_l

    def get_meta_data(self):
        """ extra data needed for inventory """
        q = f"""
        select
            i.id,
            i."purchase-rate" ,
            d."drug-name"
        from
            "prod2-generico"."prod2-generico"."inventory-1" i
        left join "prod2-generico"."prod2-generico".drugs d on
            i."drug-id" = d.id
        where
            i."store-id" in ({self.csv_store_ids})
        """
        return self.db.get_df(query=q)

    # @profile
    def start_data_fetch(self):
        """ calls all the function which fetch the data from database """
        print("Starting data fetch.")
        self.opening()
        print("opening: Successfully fetched.")
        self.purchased()
        print("purchased: Successfully fetched.")
        self.customer_returns()
        print("customer_returns: Successfully fetched.")
        self.xin()
        print("xin: Successfully fetched.")
        self.xout()
        print("xout: Successfully fetched.")
        self.sold()
        print("sold: Successfully fetched.")
        self.returned_to_dc()
        print("returned_to_dc: Successfully fetched.")
        self.deleted()
        print("deleted: Successfully fetched.")
        self.closing()
        print("closing: Successfully fetched.")
        self.audit_recon()
        print("audit_recon: Successfully fetched.")
        self.reverted_returns()
        print("reverted_returns: Successfully fetched.")

    # @profile
    def concat(self):
        """ data fetching from database """

        self.start_data_fetch()

        """
        ## combine initial and received
        temp_l = select(p_l, :id, :barcode, :p => :o, :ptr)
        recon_l = vcat(o_l, temp_l)
        ## following handles inventory lying in inventory-1 but received later
        recon_l = remove_duplicates(recon_l, "o")

        recon_l = combine_cr(recon_l, cr_l)
        recon_l = combine_xin(recon_l, xin_l)
        recon_l = combine_xout(recon_l, xout_l)
        recon_l = combine_sold(recon_l, sold_l)
        recon_l = combine_ret(recon_l, ret_l)
        recon_l = combine_ar(recon_l, ar_l)
        recon_l = combine_rr(recon_l, rr_l)
        recon_l = leftjoin(recon_l, select(del_l, :id, :del), on = :id)
        recon_l = leftjoin(recon_l, select(c_l, :id, :c), on = :id)
        """
        """ combine initial and received and call it opening(o) """
        self.p_l.rename(columns={'p': 'o'}, inplace=True)
        """ following handles inventory lying in inventory-1 but received later """
        self.recon_l = pd.concat([self.p_l, self.o_l], ignore_index=True)
        self.recon_l = remove_duplicates(self.recon_l, "o")

        """combine_cr: following handles the case where inventory was stock transferred, 
        after the start time and returned before end time """
        self.recon_l = pd.merge(self.recon_l, self.cr_l, on='id', how='outer')
        self.take_union()

        """combine_xin: this will take care of stores own inventory coming back"""
        self.recon_l = pd.merge(self.recon_l, self.xin_l, on='id', how='outer')
        self.take_union()

        """combine_xout: this will take care of stores own inventory transferred out"""
        self.recon_l = pd.merge(self.recon_l, self.xout_l, on='id', how='outer')
        self.take_union()

        """combine_sold: this will take care of stores inventory sold """
        self.recon_l = pd.merge(self.recon_l, self.sold_l, on='id', how='outer')
        self.take_union()

        """combine_ret: this will take care of stores inventory returned """
        self.recon_l = pd.merge(self.recon_l, self.ret_l, on='id', how='outer')
        self.take_union()

        """combine_ar: """
        self.recon_l = pd.merge(self.recon_l, self.ar_l, on='id', how='outer')
        self.take_union()

        """combine_rr: """
        self.recon_l = pd.merge(self.recon_l, self.rr_l, on='id', how='outer')
        self.take_union()

        self.recon_l = pd.merge(self.recon_l, self.del_l, on='id', how='left')
        self.take_union()

        self.recon_l = pd.merge(self.recon_l, self.c_l, on='id', how='left')
        self.take_union()

        """ calculate the error """
        self.recon_l = self.recon_l.fillna(0)

        for col in ['o', 'cr', 'xin', 'xout', 'ret', 'sold', 'del', 'ar', 'rr', 'c', 'barcode']:
            self.recon_l[col] = pd.to_numeric(self.recon_l[col])
            self.recon_l[col] = self.recon_l[col].astype('int', errors='raise')

        self.recon_l['e'] = self.recon_l['o'] + self.recon_l['cr'] + self.recon_l['xin'] - self.recon_l['xout'] - \
                            self.recon_l['ret'] - self.recon_l['sold'] - self.recon_l['del'] + self.recon_l['ar'] + \
                            self.recon_l['rr'] - self.recon_l['c']

        return self.recon_l
