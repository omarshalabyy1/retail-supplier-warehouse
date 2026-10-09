-- One row per category code, with the department the report shows (the client's departments file).
select
    category_code,
    department
from {{ source('bronze', 'departments') }}
