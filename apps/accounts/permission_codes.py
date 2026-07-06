"""
Códigos oficiais de permissão do PortalK12.

Regra de projeto:
- Use sempre estes códigos nas views, services e templates.
- Não espalhe strings soltas como "students.view" pelo código.
- No futuro, estes códigos alimentarão grupos configuráveis por escola.
"""

# Alunos
STUDENTS_VIEW = "students.view"
STUDENTS_CREATE = "students.create"
STUDENTS_UPDATE = "students.update"
STUDENTS_DELETE = "students.delete"
STUDENTS_MANAGE = "students.manage"

# Responsáveis / família
GUARDIANS_VIEW = "guardians.view"
GUARDIANS_CREATE = "guardians.create"
GUARDIANS_UPDATE = "guardians.update"
GUARDIANS_DELETE = "guardians.delete"
GUARDIANS_MANAGE = "guardians.manage"

# Professores
TEACHERS_VIEW = "teachers.view"
TEACHERS_CREATE = "teachers.create"
TEACHERS_UPDATE = "teachers.update"
TEACHERS_DELETE = "teachers.delete"
TEACHERS_MANAGE = "teachers.manage"

# Turmas
CLASSES_VIEW = "classes.view"
CLASSES_CREATE = "classes.create"
CLASSES_UPDATE = "classes.update"
CLASSES_DELETE = "classes.delete"
CLASSES_MANAGE = "classes.manage"

# Colaboradores
COLLABORATORS_VIEW = "collaborators.view"
COLLABORATORS_CREATE = "collaborators.create"
COLLABORATORS_UPDATE = "collaborators.update"
COLLABORATORS_DELETE = "collaborators.delete"
COLLABORATORS_MANAGE = "collaborators.manage"

# Visitantes / portaria
VISITORS_VIEW = "visitors.view"
VISITORS_CREATE = "visitors.create"
VISITORS_UPDATE = "visitors.update"
VISITORS_DELETE = "visitors.delete"
VISITORS_MANAGE = "visitors.manage"

# Cantina
CANTINA_VIEW = "cantina.view"
CANTINA_PRODUCTS_MANAGE = "cantina.products.manage"
CANTINA_ORDERS_VIEW = "cantina.orders.view"
CANTINA_ORDERS_MANAGE = "cantina.orders.manage"
CANTINA_MANAGE = "cantina.manage"

# Arquivos
FILES_VIEW = "files.view"
FILES_UPLOAD = "files.upload"
FILES_DELETE = "files.delete"
FILES_MANAGE = "files.manage"

# Comunicações
MESSAGES_VIEW = "messages.view"
MESSAGES_SEND = "messages.send"
MESSAGES_READ_RECEIPTS_VIEW = "messages.read_receipts.view"
MESSAGES_MANAGE = "messages.manage"

# Escola / configurações
SCHOOL_VIEW = "school.view"
SCHOOL_SETTINGS_UPDATE = "school.settings.update"
SCHOOL_USERS_MANAGE = "school.users.manage"
SCHOOL_PERMISSIONS_MANAGE = "school.permissions.manage"
SCHOOL_ADMIN_GRANT = "school.admin.grant"

# Auditoria
AUDITLOG_VIEW = "auditlog.view"
AUDITLOG_EXPORT = "auditlog.export"

# Administração global PortalK12
SYSTEM_ADMIN = "system.admin"
SYSTEM_SCHOOLS_MANAGE = "system.schools.manage"
SYSTEM_USERS_SUPPORT = "system.users.support"


ALL_PERMISSION_CODES = (
    STUDENTS_VIEW,
    STUDENTS_CREATE,
    STUDENTS_UPDATE,
    STUDENTS_DELETE,
    STUDENTS_MANAGE,
    GUARDIANS_VIEW,
    GUARDIANS_CREATE,
    GUARDIANS_UPDATE,
    GUARDIANS_DELETE,
    GUARDIANS_MANAGE,
    TEACHERS_VIEW,
    TEACHERS_CREATE,
    TEACHERS_UPDATE,
    TEACHERS_DELETE,
    TEACHERS_MANAGE,
    CLASSES_VIEW,
    CLASSES_CREATE,
    CLASSES_UPDATE,
    CLASSES_DELETE,
    CLASSES_MANAGE,
    COLLABORATORS_VIEW,
    COLLABORATORS_CREATE,
    COLLABORATORS_UPDATE,
    COLLABORATORS_DELETE,
    COLLABORATORS_MANAGE,
    VISITORS_VIEW,
    VISITORS_CREATE,
    VISITORS_UPDATE,
    VISITORS_DELETE,
    VISITORS_MANAGE,
    CANTINA_VIEW,
    CANTINA_PRODUCTS_MANAGE,
    CANTINA_ORDERS_VIEW,
    CANTINA_ORDERS_MANAGE,
    CANTINA_MANAGE,
    FILES_VIEW,
    FILES_UPLOAD,
    FILES_DELETE,
    FILES_MANAGE,
    MESSAGES_VIEW,
    MESSAGES_SEND,
    MESSAGES_READ_RECEIPTS_VIEW,
    MESSAGES_MANAGE,
    SCHOOL_VIEW,
    SCHOOL_SETTINGS_UPDATE,
    SCHOOL_USERS_MANAGE,
    SCHOOL_PERMISSIONS_MANAGE,
    SCHOOL_ADMIN_GRANT,
    AUDITLOG_VIEW,
    AUDITLOG_EXPORT,
    SYSTEM_ADMIN,
    SYSTEM_SCHOOLS_MANAGE,
    SYSTEM_USERS_SUPPORT,
)
