import contextvars


workspace_id = contextvars.ContextVar('workspace_id')
workspace = contextvars.ContextVar('workspace')
table_id = contextvars.ContextVar('table_id')
hfi_frequency = contextvars.ContextVar('hfi_frequency')
disable_template_security_validation = contextvars.ContextVar('disable_template_security_validation')
