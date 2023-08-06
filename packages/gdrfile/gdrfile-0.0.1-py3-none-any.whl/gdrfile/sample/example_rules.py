import rules
from rules.predicates import is_authenticated


rules.add_perm('{{app_name}}.view_{{mainclass}}', is_authenticated)
rules.add_perm('{{app_name}}.add_{{mainclass}}', is_authenticated)
rules.add_perm('{{app_name}}.change_{{mainclass}}', is_authenticated)
rules.add_perm('{{app_name}}.delete_{{mainclass}}', is_authenticated)
rules.add_perm('{{app_name}}.list_{{mainclass}}', is_authenticated)
