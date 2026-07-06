# PortalK12 — Controle de Acesso e Auditoria

## Objetivo

O PortalK12 deve nascer como uma plataforma escolar multiusuário, multiescola, auditável e preparada para LGPD.

Todo módulo deve responder:

- quem pode ver;
- quem pode criar;
- quem pode editar;
- quem pode excluir;
- qual escola é dona do dado;
- qual aluno/responsável pode acessar o dado;
- qual professor/colaborador pode acessar o dado;
- quais ações precisam de auditoria;
- quais registros devem usar exclusão lógica em vez de exclusão física.

## Princípios

1. Menor privilégio possível.
2. Escopo obrigatório por escola.
3. Responsável só acessa alunos vinculados.
4. Aluno só acessa dados próprios.
5. Professor deve acessar apenas o que sua função permitir.
6. Diretor Master administra a escola.
7. Diretor Master pode delegar administração escolar.
8. Ninguém deve conceder permissão que não possui.
9. Alterações sensíveis devem gerar log de auditoria.
10. Dados críticos devem usar soft delete.

## Perfis principais

- Super Admin PortalK12
- Diretor Master da Escola
- Administrador Escolar Delegado
- Coordenador
- Secretaria
- Professor
- Colaborador
- Portaria
- Cantina
- Responsável
- Aluno

## Modelo de permissão futuro

O modelo final será híbrido:

1. Papel base do usuário.
2. Grupos configuráveis por escola.
3. Permissões individuais.
4. Bloqueios individuais.
5. Auditoria de alterações.

Exemplo de permissões:

- students.view
- students.create
- students.update
- students.delete
- teachers.view
- teachers.create
- visitors.create
- cantina.products.manage
- messages.send
- messages.read_receipts.view
- school.permissions.manage
- school.admin.grant
- auditlog.view

## Diretor Master

O primeiro cadastro administrativo da escola deve ser o Diretor Master.

Ele pode:

- configurar a escola;
- criar usuários;
- criar grupos;
- conceder permissões;
- delegar outro Administrador Escolar;
- acompanhar auditoria da escola.

## Administrador Escolar Delegado

É um usuário que recebeu poderes administrativos do Diretor Master.

Regras:

- atua apenas dentro da escola;
- não pode alterar dados globais do PortalK12;
- não pode acessar escolas de terceiros;
- suas ações devem ser auditadas;
- permissões concedidas devem respeitar limites configurados.

## Auditoria obrigatória

Ações que devem gerar log:

- criação, edição e exclusão de aluno;
- criação, edição e exclusão de professor;
- criação, edição e exclusão de responsável;
- criação, edição e exclusão de colaborador;
- criação, edição e exclusão de visitante;
- alteração de permissões;
- criação/remoção de usuários;
- alteração de senha;
- login e falha de login;
- envio de mensagem;
- leitura de mensagem;
- upload e exclusão de arquivos;
- pedidos e alterações na cantina;
- alterações em dados da escola.

## Perguntas que a auditoria deve responder

- Quem fez?
- O que fez?
- Quando fez?
- Em qual escola?
- Em qual módulo?
- Em qual registro?
- Qual era o valor anterior?
- Qual ficou o valor novo?
- Qual IP?
- Qual navegador/dispositivo?
- A ação foi permitida por qual permissão?

## Soft delete

Registros críticos não devem ser apagados diretamente sem rastro.

Campos recomendados:

- is_active
- deleted_at
- deleted_by
- delete_reason

Exemplos:

- Aluno
- Professor
- Responsável
- Colaborador
- Visitante
- Turma
- Arquivos/documentos

## Comunicação e rastreabilidade

Mensagens devem registrar:

- quem enviou;
- para quem foi enviada;
- quando foi enviada;
- quando foi lida;
- quem leu;
- quem ainda não leu;
- se havia anexo;
- se exigia confirmação.

Exemplo de pergunta que o sistema deve responder:

"O aluno não viu a mensagem de entrega de trabalho?"

O sistema deve mostrar:

- mensagem criada;
- destinatários;
- entrega;
- leitura;
- data/hora;
- usuário que visualizou.

## Regra de desenvolvimento

Nenhum módulo novo deve ser considerado pronto sem:

- permissão de acesso;
- escopo por escola;
- regra de visibilidade para aluno/responsável, quando aplicável;
- previsão de auditoria;
- teste básico de acesso.
