if not called_on_Load:
    cartlog("termidset",dump_table(myconn, "global_term_catalogue", ""))
    cartlog("nodelete",dump_table(myconn, "global_term_catalogue", ""))


