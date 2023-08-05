# Queries for MIS

sales_query = """
            select
                a."bill-id",
                f."store-id",
                c."id" as "drug-id",
                c."drug-name",
                c."type",
                c."category",
                c."company",
                a."created-at",
                a."quantity",
                b."id" as "inventory-id",
                b."mrp",
                b."ptr" AS "zp-ptr",
                b."ptr" AS "final-ptr",
                b."purchase-rate" AS "wc-ptr",
                a."rate",
                a."cgst-rate",
                a."sgst-rate",
                a."igst-rate",
                f."payment-method",
                f."net-payable",
                f."patient-id",
                (a."rate" * a."quantity") as "value"
            from
                {schema}."bills-1{suffix_to_table}" f
            join {schema}."bill-items-1{suffix_to_table}" a on
                f."id" = a."bill-id"
            left join {schema}."inventory-1{suffix_to_table}" b on
                a."inventory-id" = b."id"
            left join {schema}."drugs{suffix_to_table}" c on
                c."id" = b."drug-id"
            left join {schema}."stores{suffix_to_table}" d on
                d."id"= b."store-id"
            where
                a."created-at" >= '{analysis_start_time}'
                and  a."created-at" <= '{analysis_end_time}'
                -- and f."store-id" = 2
            """

customer_returns_query = """
    SELECT
        b."return-id",
        b."bill-id",
        b."bill-id" as "returned-bill-id",
        a."store-id",
        a."patient-id",
        a."total-items",
        a."return-value",
        b."inventory-id",
        b."returned-quantity",
        b."cgst-rate",
        b."sgst-rate",
        b."igst-rate",
        b."rate",
        b."return-value",
        b."billed-at",
        b."returned-at",
        c."drug-id",
        c."drug-id" as "returned-drug-id",
        d."type",
        d."category",
        d."company",
        c."mrp",
        c."ptr" AS "zp-ptr",
        c."ptr" AS "final-ptr",
        c."purchase-rate" AS "wc-ptr",
        e."payment-method"
    FROM
        {schema}."customer-returns-1{suffix_to_table}" a
    JOIN {schema}."customer-return-items-1{suffix_to_table}" b ON
        a."id" = b."return-id"
    LEFT JOIN {schema}."inventory-1{suffix_to_table}" c ON
        c."id" = b."inventory-id"
    LEFT JOIN {schema}."drugs{suffix_to_table}" d ON
        d."id" = c."drug-id"
    LEFT JOIN {schema}."bills-1{suffix_to_table}" e ON
        e."id" = b."bill-id"
    WHERE
        b."returned-at" >='{analysis_start_time}' AND 
      b."returned-at" <= '{analysis_end_time}'
        -- AND a."store-id" = 2
  """

order_source_query = """
           select
                pso."bill-id" as "zeno_bill_id",
                "order-source"
            from
                {schema}."patients-store-orders{suffix_to_table}" pso
            where
                "order-source" = 'zeno'
                and
                pso."bill-id" is not null
            group by
                pso."bill-id",
                "order-source"
        """

store_list_query = """
            SELECT
                "id" AS "store-id",
                "name" AS "store-name"
            FROM
                {schema}."stores{suffix_to_table}"
            """

inventory_query = """
        select
            a."store-id",
            a."drug-id",
            (a."quantity"+ 
                a."locked-for-check" + 
                a."locked-for-audit" + 
                a."locked-for-return" + 
                a."locked-for-transfer") as "quantity",
            a."ptr" AS "final-ptr",
            a."expiry",
            "drug-name",
            "type",
            "category",
            "company",
            a."created-at",
            c."vat"
        from
            {schema}."inventory-1{suffix_to_table}" a
        left join {schema}."drugs{suffix_to_table}" b on
            a."drug-id" = b."id"
        left join {schema}."invoice-items-1{suffix_to_table}" c on
            a."invoice-item-id" = c."id"
        where
            (a."quantity"> 0
            OR a."locked-for-check" > 0
            OR a."locked-for-audit" > 0
            OR a."locked-for-return" > 0
            OR a."locked-for-transfer" > 0 )
"""

customers_initial_bill_date = """
    select
        f."patient-id",
        f."store-id",
        min (f."created-at") as "created-at"
    from
        {schema}."bills-1{suffix_to_table}" f
    group by
        f."patient-id" ,
        f."store-id"
"""

purchase_from_wc_query = """
    select
        i."franchisee-invoice-item-id",
        b."franchisee-invoice-id",
        b."invoice-id",
        a."invoice-date",
        a."created-at",
        a."store-id",
        b."drug-id",
        c."type",
        c."category",
        c."company",
        b."actual-quantity",
        b."net-value" as "zp_received_net_value",
        b."vat" as "zp_vat",
        i."net-value" ,
        i."actual-quantity"  as "1_actual_quantity",
        b."actual-quantity" as "2_actual_quantity",
        i."vat" as "wc_vat"
    from
        {schema}."invoices-1{suffix_to_table}" a
    join
            {schema}."invoice-items-1{suffix_to_table}" b on
        a."id" = b."franchisee-invoice-id"
    left join
            {schema}."drugs{suffix_to_table}" c on
        c."id" = b."drug-id"
    join
            {schema}."invoice-items{suffix_to_table}" i on
        i."id" = b."invoice-item-reference"
    where
        a."invoice-date" >= '{analysis_start_time}'
        and a."invoice-date"<= '{analysis_end_time}'
        and status not in ('live' , 'inbox')
        -- and a."store-id" = 2
"""

zippin_return_data_query = """
        select
            date(d."dispatched-at") as "dispatch-date",
            e."name",
            d."serial" as "debit-note",
            d."credit-note-reference",
            d."status",
            d."store-id",
            s."name" as "cost-centre",
            e."gstn",
            r."id" as "return-item-id",
            r."taxable" as "taxable-value",
            r."gst" as "tax-rate",
            r."gst-amount" as "tax-value",
            r."net" as "net-value",
            e."id" as "distributor-id",
            d.id as "debit-note-id",
            y."drug-id",
            p."type",
            p."category",
            p."company"
        from
            {schema}."return-items-1{suffix_to_table}" r
        left join {schema}."inventory-1{suffix_to_table}" y on
            y."id" = r."inventory-id"
        left join {schema}."drugs{suffix_to_table}" p on
            p."id" = y."drug-id"
        join {schema}."debit-notes-1{suffix_to_table}" d on
            r."debit-note-reference" = d."id"
        join {schema}."distributors{suffix_to_table}" e on
            d."dist-id" = e."id"
        join {schema}."stores{suffix_to_table}" s on
            d."store-id" = s."id"
        where
            d."dispatched-at">='{analysis_start_time}'
            and d."dispatched-at"<= '{analysis_end_time}'
            and d."dist-id" != 64
"""

workcell_return_data_query = """
        select
            date(d."dispatched-at") as "dispatch-date",
            d."created-at" as "created-date",
            e."name",
            d."serial" as "debit-note",
            d."credit-note-reference",
            d."status",
            d."store-id",
            s."name" as "cost-centre",
            e."gstn",
            r."id" as "return-item-id",
            r."taxable" as "taxable-value",
            r."gst" as "tax-rate",
            r."gst-amount" as "tax-value",
            r."net" as "net-value",
            y."drug-id",
            o."type",
            o."category",
            o."company"
        from
            {schema}."return-items{suffix_to_table}" as r
        left join {schema}."inventory{suffix_to_table}" y on
            r."inventory-id"= y."id"
        left join {schema}."drugs{suffix_to_table}" o on
            o."id" = y."drug-id"
        join {schema}."debit-notes{suffix_to_table}" as d on
            r."debit-note-reference" = d."id"
        join {schema}."distributors{suffix_to_table}" as e on
            d."dist-id" = e."id"
        join {schema}."stores{suffix_to_table}" as s on
            d."store-id" = s."id"
        where
            d."dispatched-at">='{analysis_start_time}'
            and d."dispatched-at"<='{analysis_end_time}'
"""

local_purchase_data_query = """
        select
            a."id" as "inventory-id",
            "invoice-reference",
            b."franchisee-invoice-id",
            c."distributor-id",
            x."name",
            a."store-id",
            s."name" as "store-name",
            a."drug-id",
            d."drug-name",
            d."type",
            d."category",
            d."company",
            "vat",
            b."actual-quantity",
            b."net-value",
            a."ptr",
            a."purchase-rate",
            a."created-at",
            c."dispatch-status"
        from
            {schema}."inventory-1{suffix_to_table}" a
        join
                {schema}."invoice-items-1{suffix_to_table}" b on
            a."invoice-item-id" = b."id"
        left join
               {schema}."invoices-1{suffix_to_table}" c on
            a."franchisee-invoice-id" = c."id"
        left join
                {schema}."drugs{suffix_to_table}" d on
            a."drug-id" = d."id"
        left join
                {schema}."stores{suffix_to_table}" s on
            s."id" = a."store-id"
        left join 
                {schema}."distributors{suffix_to_table}" x on
            x."id" = c."distributor-id"
        where
            "invoice-reference" is null
            and a."created-at" >= '{analysis_start_time}'
            and a."created-at" <= '{analysis_end_time}'
"""

generic_composition_count_query = """
    select
        count(distinct t."composition") as "count"
    from
        (
        select
            "id",
            "drug-name",
            "type",
            "composition"
        from
             {schema}."drugs{suffix_to_table}"
        where
            "type" = 'generic'
            and "composition" != ''
            ) t
"""

ethical_margin_query = """
     select
        sum(a."actual-quantity" * a."mrp") as "value1",
        sum(a."net-value") as "net-value"
    from
        {schema}."invoice-items{suffix_to_table}" a
    join {schema}."invoices{suffix_to_table}" b on
        a."invoice-id" = b."id"
    join {schema}."distributors{suffix_to_table}" c on
        c."id" = b."distributor-id" 
    join {schema}."drugs{suffix_to_table}" d on
        d."id" = a."drug-id"
    where
        c."credit-period">0
        and d."type" = 'ethical'
        and a."created-at" >= '{analysis_start_time}'
        and a."created-at" <= '{analysis_end_time}'
    group by
        date_part(year, a."created-at"),
        date_part (month,a."created-at")
"""

home_delivery_data_query = """
    select
        pso."order-number",
        pso.id as "patient-store-order-id",
        pso."patient-request-id",
        pso."zeno-order-id" ,
        pso."patient-id" ,
        pso."order-source" as "order-source-pso" ,
        pso."order-type" ,
        pso."status" as "pso-status",
        pso."created-at" as "pso-created-at", 
        pso."store-id" ,
        s."name" as "store-name",
        pso."drug-id" ,
        pso."drug-name" ,
        pso."requested-quantity", 
        pso."inventory-quantity" as "inventory-at-creation", 
        pr."required-quantity", 
        pr."quantity-to-order",
        pso."bill-id",
        b."created-at" as "bill-date",
        dt."delivered-at",
        ss."type" as "slot-type"
    from
        {schema}."patients-store-orders{suffix_to_table}" pso
    left join {schema}."patient-requests{suffix_to_table}" pr on
        pso."patient-request-id" = pr.id
    join {schema}."stores{suffix_to_table}" s on
        s."id" = pso."store-id"
    left join {schema}."bills-1{suffix_to_table}" b on
        b."id" = pso."bill-id"
    left join {schema}."delivery-tracking{suffix_to_table}" dt 
                        on
        dt."patient-store-order-id" = pso."id"
    left join {schema}."store-slots{suffix_to_table}" ss 
                  on
        pso."slot-id" = ss.id
    where
        dt."delivered-at" >= '{analysis_start_time}'
        and dt."delivered-at"<= '{analysis_end_time}'
        and pso."order-type" = 'delivery'
        and pso."bill-id" is not null
    order by
        pso."created-at" desc
"""

delivery_bill_ids_query = """
    select
        "bill-id"
    from
        {schema}."patients-store-orders{suffix_to_table}" pso
    where
        pso."order-type" = 'delivery'
    group by
        "bill-id"
"""

cumulative_consumers_data_query = """
    select
        f."store-id" ,
        count(distinct "patient-id") as "total-cons",
        count(distinct case
            when c.company != 'GOODAID' and c."type" in ('generic', 'high-value-generic') then "patient-id"
        end) as "generic-without-gaid-cons",
        count(distinct case
            when c."type" in ('generic', 'high-value-generic') then "patient-id"
        end) as "generic-cons",
        count(distinct case
            when c.company in ('GOODAID') then "patient-id"
        end) as "total-gaid-cons",
        count(distinct case
            when c.category in ('chronic') then "patient-id"
        end) as "total-chronic-cons"
    from
        {schema}."bills-1{suffix_to_table}" f
    join {schema}."bill-items-1{suffix_to_table}" a on
        f."id" = a."bill-id"
    left join {schema}."inventory-1{suffix_to_table}" b on
        a."inventory-id" = b."id"
    left join {schema}."drugs{suffix_to_table}" c on
        c."id" = b."drug-id"
    -- where
       -- f."store-id" = 2
    group by
        f."store-id"
"""

other_files_ethical_margin_query = """
    select
        date_part (year,
        a."created-at") as "year",
        date_part(month, a."created-at") as "month",
        sum(a."actual-quantity" * a."mrp") as "actual-quantity * mrp",
        sum(a."net-value") as "net-value"
    from
        {schema}."invoice-items{suffix_to_table}" a
    join {schema}."invoices{suffix_to_table}" b on
        a."invoice-id" = b."id"
    join {schema}."distributors{suffix_to_table}" c on
        c."id" = b."distributor-id"
    join {schema}."drugs{suffix_to_table}" d on
        d."id" = a."drug-id"
    where
        c."credit-period">0
        and d."type" = 'ethical'
        and date(a."created-at") >= '2021-08-01'
    group by
        date_part(year, a."created-at"),
        date_part(month, a."created-at")
"""

other_files_distributor_margin_query = """
    select
        date_part(year,a."created-at") as "year",
        date_part(month,a."created-at") as "month",
        c."name",
        sum(a."actual-quantity"* a."mrp") as "actual-quantity * mrp",
        sum(a."net-value") as "net-value"
    from
        {schema}."invoice-items{suffix_to_table}" a
    join {schema}."invoices{suffix_to_table}" b on
        a."invoice-id"= b."id"
    join {schema}."distributors{suffix_to_table}" c on
        c."id"= b."distributor-id"
    join {schema}."drugs{suffix_to_table}" d on
        d."id"= a."drug-id"
    where
        c."credit-period">0
        and date_part (year ,a."created-at") = {choose_year}
        and date_part (month ,a."created-at") = {choose_month}
    group by
        date_part (year,a."created-at"),
        date_part (month,a."created-at"),
        c."name"
"""

other_files_inventory_at_dc_near_expiry_data_query = """
    select
        a."invoice-number",
        b."invoice-id",
        b."vat",
        a."invoice-date",
        a."store-id",
        b."drug-id",
        a."net-payable",
        b."net-value",
        case
            when b."actual-quantity" = 0 then 0
            else
        (b."net-value"*1.0 / b."actual-quantity"*1.0)
        end as "final-ptr",
        b."actual-quantity",
        a."created-at",
        a."received-at",
        "status",
        "dispatch-status",
        c."type",
        c."category",
        b."expiry"
    from
        {schema}."invoices{suffix_to_table}" a
    join {schema}."invoice-items{suffix_to_table}" b on
        a."id" = b."invoice-id"
    join {schema}."drugs{suffix_to_table}" c on
        b."drug-id" = c."id"
    where
        "status" = 'approved'
        and "dispatch-status" in ('dispatch-status-na')
"""


goodaid_store_sales_query = """
    select
        date_part (year,
        b."created-AT") as "YEAR",
        date_part (month,
        b."created-AT") as "MONTH",
        b."store-id",
        max(s."name") as "store-name",
        SUM(c."mrp" * a."quantity") as "gross_mrp",
        SUM((c."mrp" * a."quantity") / 
        (1 + ((a."cgst-rate" + a."sgst-rate")/ 100))) as "gross_mrp_taxable",
        SUM(a."rate" * a."quantity") as "gross_revenue",
        SUM((a."rate" * a."quantity") / 
        (1 + ((a."cgst-rate" + a."sgst-rate")/ 100))) as "gross_revenue_taxable",
        SUM(c."purchase-rate" * a."quantity") as "gross_cogs",
        SUM((c."purchase-rate" * a."quantity") / 
        (1 + ((a."cgst-rate" + a."sgst-rate")/ 100))) as "gross_cogs_taxable",
        sum(a."quantity") as "gross_quantity"
    from
        {schema}."bill-items-1{suffix_to_table}" a
    left join {schema}."bills-1{suffix_to_table}" b on
        b."id" = a."bill-id"
    left join {schema}."inventory-1{suffix_to_table}" c on
        c."id" = a."inventory-id"
    left join {schema}."stores{suffix_to_table}" s on
        s."id" = b."store-id"
    left join {schema}."drugs{suffix_to_table}" d on
        d."id" = c."drug-id"
    where
        date_part (year,
        a."created-AT") = {choose_year}
        and 
        date_part (month,
        a."created-AT") ={choose_month}
        and 
        d."company" = 'GOODAID'
    group by
        date_part(year, b."created-AT"),
        date_part(month, b."created-AT"),
        b."store-id"
"""

goodaid_store_returns_query = """
    select
        date_part (year,b."returned-at") as "year",
        date_part (month,b."returned-at") as "month",
        b."store-id",
        max(s."name") as "store-name",
        (SUM(c."mrp" * a."returned-quantity") * -1) as "returns_mrp",
        (SUM((c."mrp" * a."returned-quantity") / 
        (1 + ((a."cgst-rate" + a."sgst-rate")/ 100))) * -1) as "returns_mrp_taxable",
        (SUM(a."rate" * a."returned-quantity") * - 1) as "returns",
        (SUM((a."rate" * a."returned-quantity") / 
        (1 + ((a."cgst-rate" + a."sgst-rate")/ 100))) * -1) as "returns_taxable",
        (SUM(c."purchase-rate" * a."returned-quantity") * -1) as "returns_cogs",
        (SUM((c."purchase-rate" * a."returned-quantity") / 
        (1 + ((a."cgst-rate" + a."sgst-rate")/ 100))) * -1) as "returns_cogs_taxable",
        (sum(a."returned-quantity") * -1) as "returned_quantity"
    from
        {schema}."customer-return-items-1{suffix_to_table}" a
    left join {schema}."customer-returns-1{suffix_to_table}" b on
        b."id" = a."return-id"
    left join {schema}."inventory-1{suffix_to_table}" c on
        c."id" = a."inventory-id"
    left join {schema}."stores{suffix_to_table}" s on
        s."id" = b."store-id"
    left join {schema}."drugs{suffix_to_table}" d on
        d."id" = c."drug-id"
    where
        date_part(year,a."returned-at") = {choose_year}
        and 
        date_part(month,a."returned-at") = {choose_month}
        and 
        d."company" = 'GOODAID'
    group by
        date_part(year,b."returned-at"),
        date_part(month,b."returned-at"),
        b."store-id"
"""

goodaid_zippin_inventory_query = """
    select
        a."store-id",
        s."name" as "store-name",
        a."drug-id",
        b."drug-name",
        b."type",
        b."category",
        a."expiry",
        c."vat",
        ((a."quantity"+ a."locked-for-check" + a."locked-for-audit" + 
          a."locked-for-return" + a."locked-for-transfer")) as "quantity",
        ((a."quantity"+ a."locked-for-check" + a."locked-for-audit" + 
          a."locked-for-return" + a."locked-for-transfer") * a."ptr") as "value",
        a."ptr",
        a."created-at"
    from
        {schema}."inventory-1{suffix_to_table}" a
    join {schema}."invoice-items-1{suffix_to_table}" c on
        a."invoice-item-id" = c."id"
    left join {schema}."drugs{suffix_to_table}" b on
        a."drug-id" = b."id"
    left join {schema}."stores{suffix_to_table}" s on
        s."id" = a."store-id"
    where
        (a."quantity"> 0
            or  
        a."locked-for-check" > 0
            or 
        a."locked-for-audit" > 0
            or
        a."locked-for-return" > 0
            or
        a."locked-for-transfer" > 0)
        and b."company" = 'GOODAID'
"""


goodaid_dc_inventory_query = """
    select
        m."dc-id" as store_id,
        (
        select
            "name"
        from
            {schema}."stores{suffix_to_table}"
        where
            id = m."dc-id"
        limit 1) as store_name,
        vat,
        sum("post_tax") post_tax,
        sum(taxable_amount) as taxable_amount
    from
        (
        select 
            a."store-id",
            (
            select
                "forward-dc-id"
            from
                {schema}."store-dc-mapping{suffix_to_table}"
            where
                max(dgs.type) = "drug-type"
                and "store-id" = a."store-id"
            limit 1) as "dc-id",
            round(sum( coalesce (a."locked-quantity" * "purchase-rate", 0) )) "post_tax",
            b.vat,
            round(sum(coalesce (a."locked-quantity" * a."purchase-rate", 0) / (1 + b.vat / 100) )) as "taxable_amount"
        from
            {schema}."inventory{suffix_to_table}" a
        join {schema}."invoice-items{suffix_to_table}" b on
            a."invoice-item-id" = b.id
        join {schema}."drugs{suffix_to_table}" dgs on
            dgs.id = a."drug-id"
        where
            "dgs"."company" = 'GOODAID'
        group by
            a."store-id",
            b.vat 
    union
        select
            a."store-id",
            (
            select
                "forward-dc-id"
            from
                {schema}."store-dc-mapping{suffix_to_table}"
            where
                max(dgs."type") = "drug-type"
                and "store-id" = a."store-id"
            limit 1) as "dc-id",
            round(sum( coalesce (a."locked-quantity" * "purchase-rate", 0) )) "post_tax",
            b.vat,
            round(sum( coalesce (a."locked-quantity" * a."purchase-rate", 0) / (1 + b.vat / 100) )) as "taxable_amount"
        from
            {schema}."inventory-1{suffix_to_table}" a
        join {schema}."invoice-items-1{suffix_to_table}" b on
            a."invoice-item-id" = b.id
        join {schema}."drugs{suffix_to_table}" dgs on
            dgs.id = a."drug-id"
        where
            "dgs"."company" = 'GOODAID'
        group by
            a."store-id",
            b.vat
    union
        select
            b."store-id",
            (
            select
                "return-dc-id"
            from
                {schema}."store-dc-mapping{suffix_to_table}"
            where
                max(dgs.type) = "drug-type"
                and "store-id" = b."store-id"
            limit 1) as "dc-id",
            round(sum( coalesce (a."returned-quantity" * c."purchase-rate", 0))) "post_tax",
            d.vat,
            round(sum( coalesce (a."returned-quantity" * c."purchase-rate", 0) / (1 + d.vat / 100) )) as "taxable_amount"
        from
            {schema}."return-items{suffix_to_table}" a
        join {schema}."returns-to-dc{suffix_to_table}" b on
            a."return-id" = b.id
        join {schema}."inventory{suffix_to_table}" c on
            a."inventory-id" = c.id
        join {schema}."drugs{suffix_to_table}" dgs on
            dgs.id = c."drug-id"
        join {schema}."invoice-items{suffix_to_table}" d on
            c."invoice-item-id" = d.id
        where
            a."status" in ('saved', 'approved')
                and "dgs"."company" = 'GOODAID'
            group by
                b."store-id",
                d.vat 
        ) m
    group by
        "dc-id",
        vat;
"""

goodaid_wh_inventory_query = """
    select
        "drug-id",
        "drug-name",
        sum("balance-quantity") as wh_qty,
        sum("balance-value") as wh_value
    from
        "prod2-generico"."wh-inventory-ss" wis
    where
        date("created-at") = '{date}'
    group by
        "drug-id",
        "drug-name"
"""

goodaid_drugs_query = """
    select
        "id" as "drug_id",
        "company"
    from
        {schema}."drugs{suffix_to_table}"
    where
        "company" = 'GOODAID'
"""

store_info_query = """
   select
        sm.id as "store-id",
        sm."name" as "store-name",
        case
            when sm."franchisee-id" = 1 then 'COCO'
            else 'FOFO'
        end as "franchise-flag",
        zc."name" as "city-name",
        sg."name" as "store-group-name",
        zis."name" as "state-name"
    from
        {schema}."stores{suffix_to_table}" sm
    left join "prod2-generico"."zeno-city" zc 
        on
        sm."city-id" = zc.id
    left join "prod2-generico"."store-groups" sg 
        on
        sm."store-group-id" = sg.id
    left join "prod2-generico"."zeno-indian-states" zis 
        on
        zc."indian-state-id" = zis.id
"""