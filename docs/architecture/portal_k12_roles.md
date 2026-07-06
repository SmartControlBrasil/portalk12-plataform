# PortalK12 — Papéis e Responsabilidades

## Super Admin PortalK12

Usuário global da plataforma.

Pode:

- criar escolas;
- bloquear escolas;
- gerenciar planos;
- prestar suporte técnico;
- acessar auditoria global quando necessário;
- criar ou recuperar administradores escolares.

Não representa uma escola específica.

## Diretor Master da Escola

Primeiro administrador da escola.

Pode:

- configurar dados da escola;
- gerenciar usuários;
- gerenciar permissões;
- criar grupos de acesso;
- delegar administrador escolar;
- visualizar auditoria da escola;
- gerenciar módulos escolares.

## Administrador Escolar Delegado

Pessoa autorizada pelo Diretor Master.

Pode receber permissões amplas dentro da escola.

Uso típico:

- vice-diretor;
- coordenador geral;
- responsável administrativo;
- gestor de secretaria.

## Coordenador

Pode atuar em:

- turmas;
- professores;
- alunos;
- comunicados pedagógicos;
- acompanhamento acadêmico.

As permissões exatas devem ser configuráveis pela escola.

## Secretaria

Pode atuar em:

- cadastro de alunos;
- cadastro de responsáveis;
- documentos;
- matrículas;
- comunicados administrativos.

Não deve receber permissões sensíveis por padrão, como alteração ampla de permissões.

## Professor

Pode atuar em:

- visualização dos alunos permitidos;
- turmas vinculadas;
- comunicados;
- tarefas;
- visitantes, se a escola permitir;
- materiais e arquivos, se a escola permitir.

Não pode gerenciar professores, alunos ou colaboradores por padrão.

## Colaborador

Perfil genérico para funcionários da escola.

Pode ter acesso conforme grupo:

- cantina;
- portaria;
- manutenção;
- secretaria;
- financeiro;
- limpeza;
- apoio pedagógico.

## Portaria

Pode atuar em:

- visitantes;
- entrada e saída;
- autorização de retirada;
- consulta mínima de aluno/responsável.

Não deve acessar dados pedagógicos ou financeiros por padrão.

## Cantina

Pode atuar em:

- produtos;
- cardápio;
- pedidos;
- restrições alimentares autorizadas;
- controle operacional da cantina.

Não deve acessar cadastro completo do aluno por padrão.

## Responsável

Pai, mãe ou responsável legal.

Pode acessar apenas alunos vinculados a ele.

Pode ver:

- comunicados;
- frequência;
- tarefas;
- ocorrências;
- documentos liberados;
- pedidos de cantina;
- financeiro, se habilitado.

## Aluno

Pode acessar apenas dados próprios.

Pode ver:

- comunicados;
- tarefas;
- materiais;
- agenda;
- notas/boletim, se liberado;
- cantina, se habilitado.
