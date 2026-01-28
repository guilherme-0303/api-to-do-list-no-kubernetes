# API To-Do List no Kubernetes

## Visão Geral

A **API To-Do List** é uma aplicação backend desenvolvida com **FastAPI**, com a finalidade de oferecer um serviço simples de gestão de uma lista de itens, acessível pela rota /todos. O objetivo principal foi criar uma solução que, apesar de simples, fosse o mais completa possível, focando mais na integração entre as tecnologias e menos em features interessantes, buscando colocar em prática os princípios de desenvolvimento e DevOps, com testes automatizados, integração contínua, conteinerização e orquestração.

O principal problema a ser resolvido foi colocar uma API com todas as funcionalidades CRUD dentro de um ambiente Kubernetes, com persistência de dados usando uma solução de armazenamento externa ao cluster.

## Tecnologias usadas

* FastAPI.
* uv.
* Uvicorn.
* Postgres.
* GitHub Actions.
* Kubernetes (Kind).
* NGINX Ingress Controller.
* MetalLB.

## Decisões técnicas

### FastAPI, uv e uvicorn

Dentre os frameworks do ecossistema Python, o FastAPI foi escolhido por se aproveitar bem das tendências mais recentes do desenvolvimento Python, como a tipagem e as dataclasses, e se integrar bem a testes automatizados e ao pytest através do TestClient e injeções de dependências. Já a escolha do uv se deu para entender como utilizar essa ferramenta super rápida e cheia de recursos no desenvolvimento completo, desde a inicialização do projeto até a conteinerização e o processo de integração contínua com o GitHub Actions. Por fim, o uvicorn é um servidor ASGI simples, de fácil uso.

### GitHub Actions

Para quem já possui uma conta no GitHub, é uma decisão fácil, integrando-se perfeitamente ao fluxo de desenvolvimento Git com o GitHub como repositório remoto. O yaml e as actions facilitam a escrita do pipeline. Acrescenta-se a isso a facilidade de configurar os secrets através do `gh`.

### Usar o Kind ao invés do Kubeadm

Embora o Kubeadm seja o mais robusto, e haja também o k3s, muito usado em homelabs, o Kind é o mais leve e prático. Com ele, é possível criar e deletar um cluster Kubernetes com um só comando, sem a necessidade de provisionar máquinas virtuais para serem os nós e sem a necessidade de configurar a conexão entre os nós. Sua única exigência é ter o Docker instalado, tornando-o perfeito para ambientes de testes, experimentações e aprendizado, que rodam em uma máquina só.

### Escrever do zero os manifests do Postgres

Configurar o Postgres do zero, ao invés de utilizar o Helm para implementar soluções mais robustas como o CloudNativePG ou o Zalando Postgres Operator, teve como objetivo entender as dificuldades de configurar o banco de dados em um ambiente Kubernetes. Assim, seria necessário entender os detalhes de como implementar corretamente o StatefulSet, o Persistent Volume e o Persistent Volume Claim e como interligar o Persistent Volume ao servidor NFS. Tudo isso seria abstraído pelo Helm que, em produção, facilitaria configurar outros detalhes importantes, como arquitetura de maior disponibilidade com um banco de escrita e bancos de leitura e facilitaria ajustar backups e tudo necessário para um armazenamento confiável.

### NFS e MetalLB

Ambos foram escolhidos para tentar emular aspectos de ambientes reais. O NFS foi usado para emular algo como o Elastic Block Storage da AWS e o MetalLB para emular algo como o Aplication Load Balancer. Com o NFS, seria possível ter um serviço de armazenamento externo ao cluster, acessível por diferentes nós, persistente à deleção do próprio cluster. Já o MetalLB permite acessar o cluster por um IP externo que é possível vincular a qualquer um dos serviços. No caso do Kind, é um IP alocado a partir da rede interna do Docker. Tendo o Ingress recebido um IP, é possível usar o `httpie` ou o `curl` para consumir a API. Se, além disso, for associado um domínio a esse IP no `/etc/hosts` (por exemplo, `todolist.com`) é possível escrevê-lo no manifest Ingress e acessar a API com esse domínio, assim: `http GET todolist.com/todos`. Desse modo, é possível usar o serviço LoadBalancer sem estar na núvem, não sendo mais necessário usar NodePort ou port-forwarding.

## Principais dificuldades

A maior dificuldade desse projeto, sem dúvida, foi configurar o banco de dados para funcionar no Kubernetes junto com o NFS. Dois erros pequenos foram os que levaram mais tempo para serem descobertos. O primeiro foi o uso das variáveis de ambiente. Nos tutoriais de Docker e Kubernetes, nos artigos do Medium, as variáveis de ambiente usadas para configurar o usuário e senha no Postgres através do ConfigMap são POSTGRES_USER e POSTGRES_PASSWORD. No entanto, só funcionou utilizar as variáveis PGUSER e PGPASSWORD, que constam na documentação do Postgres, [nessa seção](https://www.postgresql.org/docs/current/libpq-envars.html). Antes disso, não foi possível conectar-se ao banco de dados nem com o SQLAlchemy, na aplicação Python, nem com o psql. Ainda não é claro o motivo pelo qual isso aconteceu.

Tudo isso gerou reflexões sobre como o Postgres deveria ser configurado ou se ele é adequado ao ambiente de contêineres. Ele deve ser configurado com variáveis de ambiente mesmo ou através do SQL, criando os usuários com seus corretos privilégios? Há vantagens em usar o Postgres em contêineres? A forma como ele é configurado parece indicar que é melhor não usá-lo dessa forma. Talvez soluções como o CloudNativePG sejam a resposta.

O segundo erro foi no manifest de Secret do Postgres. Ao esquecer de usar a flag `-n`no comando `echo <secret> | base64` gerou um caracter `^J` na string do usuário e da senha, tornando inválida a autenticação. Só foi possível descobrir esse erro depois ler uma menção a ele em um fórum, podendo verificar posteriormente usando `kubectl get secret postgres-secret -o jsonpath='{.data.PGUSER}' | base64 -d`.

Mais fácil de resolver, uma outra situação que causou erros foi a configuração de permissões no NFS. O Postgres tinha problemas de permissão ao escrever no diretório exportado pelo servidor NFS. A solução foi utilizar `kubectl exec -it postgres-0 -- bash` para entrar no contêiner do Postgres e verificar qual era o ID do usuário e do grupo com `id postgres`. Tendo descoberto que o ID era 999 para ambos, foi só mudar para 999 o owner e o grupo do diretório `/data` na máquina em que estava rodando o servidor NFS, com `chown 999:999 data`, mesmo que o 999 não fosse o UID e o GID do Postgres nessa máquina.

## Principais aprendizados

Escrever os manifests mais importantes, colocar em prática conhecimentos de rede no Kubernetes, tudo isso foi importante. No entanto, o maior aprendizado foi, sem dúvida, o processo de depuração em um cluster Kubernetes. As situações de não saber o que fazer, de caçar bugs, tentar entender o próximo passo, testar hipóteses foram muito boas para adquirir de vez o costume de usar os comandos do kubectl: `kubectl get`, para ver o estado dos pods; `kubectl logs` para ler os logs da base de dados, `kubectl describe`, quando havia um erro no contêiner antes mesmo de funcionar a base de dados; `kubectl exec` para entrar no contêiner do Postgres; labels, para selecionar os pods certos; e jsonpath, para formatar a saída. Nessas situações, também se mostrou muito valioso ter escrito testes, pois, sendo conhecido que a aplicação Python estava funcionando, podia-se concluir que o único motivo pelo qual o Pod da aplicação estava em CrashLoopBackOff era a conexão com o banco de dados.

## Próximos passos e possibilidades de evolução

* Implementar autenticação na API usando tokens JWT.
* Entender como usar o Alembic fora e dentro do cluster Kuberentes, para gerenciar as migrações.
* Usar, no pipeline de integração contínua, o `docker push` para enviar a imagem para o registry ao invés de tê-la somente na máquina de desenvolvimento.
* Configurar observabilidade no cluster com Prometheus e Grafana.
* Entender melhor como funciona outras soluções de armazenamento no Kubernetes.
* Configurar um arquitetura de maior disponibilidade para o banco de dados, com réplicas de leitura.
* Entender melhor como funciona a escalabilidade dentro do Kubernetes, com HPA.
* Usar o Vault para manejar as informações sensíveis.
* Dividir a infraestrutura em desenvolvimento, homologação e produção, testando como o Kustomize e o Helm podem ajudar nessa tarefa.
