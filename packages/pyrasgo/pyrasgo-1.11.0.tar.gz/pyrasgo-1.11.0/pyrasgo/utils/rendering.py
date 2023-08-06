"""
sql rendering functions
"""
__all__ = ['operations_as_cte', 'offline_operations_as_cte']
import re
from typing import List, Dict, Any

from rasgotransforms.render import RasgoEnvironment
import pandas as pd

from pyrasgo.schemas.dw_operation import Operation, OperationCreate
from pyrasgo.schemas.transform import Transform
from pyrasgo.primitives.dataset import Dataset
from pyrasgo.utils import naming
from pyrasgo.constants import SOURCE_TABLE_ARG_NAME


def operation_as_subquery(source_code: str, source_table: str, arguments: Dict[str, Any], running_sql: str = '') -> str:
    from pyrasgo.api import Read

    def run_query(query) -> pd.DataFrame:
        query = f'{running_sql} {query}'
        result = Read().data_warehouse.query_into_dataframe(query)
        return result

    def get_columns(table: str) -> Dict[str, str]:
        if running_sql:
            return Read().data_warehouse.get_schema(f"{running_sql} SELECT * FROM {table}")
        else:
            return Read().data_warehouse.get_schema(table)

    env = RasgoEnvironment(run_query=run_query)
    return env.render(
        source_code=source_code,
        source_table=source_table,
        arguments=arguments,
        override_globals={'get_columns': get_columns},
    )


def offline_operations_as_cte(operations: List[OperationCreate], transforms: List[Transform]) -> str:
    if operations:
        transforms = {t.id: t for t in transforms}
        sql = ''
        sub_queries = []
        for i in range(len(operations)):
            arguments = replace_args(operations[i].operation_args.copy(), sub_queries)
            if transforms[operations[i].transform_id].name == 'apply':
                source_code = arguments['sql']
            else:
                source_code = transforms[operations[i].transform_id].sourceCode
            operation_sql = operation_as_subquery(
                source_code=source_code,
                source_table=arguments[SOURCE_TABLE_ARG_NAME],
                running_sql=sql,
                arguments=arguments,
            )
            sub_queries.append(operations[i].table_name)
            sql += 'WITH ' if i == 0 else ', '
            sql += f"{operations[i].table_name} as (\n{operation_sql}\n)"
        last_op = operations[-1].table_name
        sql += f' SELECT * FROM {last_op}'
        return sql


def replace_args(arguments, sub_queries):
    """
    Traverses all args recursively and replaces instances of fqtns with table names if the tables are created in the cte
    """

    def replace_string(s):
        if isinstance(s, Dataset):
            s = s.fqtn
        if isinstance(s, str) and s.split('.')[-1] in sub_queries:
            return s.split('.')[-1]
        else:
            return s

    def replace_list(l):
        l = l.copy()
        for i in range(len(l)):
            if isinstance(l[i], dict):
                l[i] = replace_dict(l[i])
            elif isinstance(l[i], list):
                l[i] = replace_list(l[i])
            else:
                l[i] = replace_string(l[i])
        return l

    def replace_dict(d):
        d = d.copy()
        for k in d.keys():
            if isinstance(d[k], dict):
                d[k] = replace_dict(d[k])
            if isinstance(d[k], list):
                d[k] = replace_list(d[k])
            else:
                d[k] = replace_string(d[k])
        return d

    return replace_dict(arguments.copy())


def operations_as_cte(
    operations: List[Operation],
) -> str:
    """
    Returns a nested CTE statement to render this op set as a CTE
    """
    # Handle single transform chains, we already have the SQL
    if len(operations) == 1:
        return operations[0].operation_sql

    # Handle multi-transform chains
    operation_list = []
    # Need to replace old FQTNs with CTE aliases
    fqtn_mapping = {}
    for operation in operations:
        # create new aliases to replace old FQTNs with
        alias = operation.dw_table.table_name or naming.random_table_name()
        fqtn_mapping[operation.dw_table.fqtn] = alias

        op_sql = operation.operation_sql

        # replace all instances of generated FQTNs with CTE aliases
        for fqtn, alias in fqtn_mapping.items():
            op_sql = op_sql.replace(fqtn, alias)

        # if final op, we're done. join ops and leave last one alone
        # Final op itself might be a CTE, remove the WITH and slap it on the end of this chain
        if operation == operations[-1]:
            return 'WITH {}{}'.format(', \n'.join(operation_list), collapse_cte(op_sql))

        operation_list.append(f'{alias} AS (\n{op_sql}\n) ')


def collapse_cte(sql: str) -> str:
    """
    Returns a collapsed CTE if the sql itself is already a CTE (starts with "with")
    """
    return re.sub(r'^(WITH)\s', ', ', sql, 1, flags=re.IGNORECASE)
